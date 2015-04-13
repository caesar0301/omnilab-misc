package cn.edu.sjtu.omnilab.emcbdc

import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.SparkContext._

import scala.collection.mutable.HashMap

case class CleanWIFILog(MAC: String, time: Long, code: Int, payload: String) // payload as AP or IP
case class WIFISession(MAC: String, stime: Long, etime: Long, AP: String)
case class IPSession(MAC: String, stime: Long, etime: Long, IP: String)

/**
 * An imitation of WIFICode.java
 */
object WIFICodeSchema {
  val AuthRequest: Int = 0
  val Deauth: Int = 1
  val AssocRequest: Int = 2
  val Disassoc: Int = 3
  val UserAuth: Int = 4
  val IPAllocation: Int = 5
  val IPRecycle: Int = 6
}

/**
 * Cleanse WIFI movement log for EMCBDC.
 */
object CleanseWIFILogJob {

  final val mergeSessionThreshold: Long = 10 * 1000

  def main(args: Array[String]): Unit = {

    if ( args.length < 2) {
      println("Usage: CleanseMovementJob <in> <out>")
      sys.exit(-1)
    }

    val input = args(0)
    val output = args(1)

    val conf = new SparkConf()
    conf.setAppName("Cleanse WIFI syslog to movement data")
    val spark = new SparkContext(conf)

    // filter and format WIFI syslog
    val inRDD = spark.textFile(input)
      .map { m => {
        val filtered = WIFILogFilter.filterData(m)
        var cleanLog: CleanWIFILog = null
        if (filtered != null) {
          val parts = filtered.split(',')
          cleanLog = CleanWIFILog(MAC = parts(0), time = Utils.ISOToUnix(parts(1)),
            code = parts(2).toInt, payload = parts(3))
        }
        cleanLog
      }}.filter(_ != null).cache

    // extract sessions
    val validSessionCodes = List(
      WIFICodeSchema.AuthRequest,
      WIFICodeSchema.AssocRequest,
      WIFICodeSchema.Deauth,
      WIFICodeSchema.Disassoc
    )

    val sessionRDD = inRDD.filter(m => validSessionCodes.contains(m.code)).sortBy(_.time)
      .groupBy(_.MAC).flatMap { case (key, logs) => { extractSessions(logs) }
    }

    val IPRDD = inRDD
      .filter( m => m.code == WIFICodeSchema.IPAllocation || m.code == WIFICodeSchema.IPRecycle)
      .groupBy(_.MAC)
      .flatMap { case (key, logs) => { collectIPSession(logs) }}

    val authRDD = inRDD.filter(m => m.code == WIFICodeSchema.UserAuth)
      .map( m => CleanWIFILog(MAC=m.MAC, time=m.time, code=m.code, payload=m.payload))
      .distinct

  }

  /**
   * Extract WIFI association sessions from certain individual's logs
   * @param logs
   * @return
   */
  def extractSessions(logs: Iterable[CleanWIFILog]): Iterable[WIFISession] = {
    var sessions = new Array[WIFISession](0)
    var APMap = new HashMap[String, Long]
    var preAP: String = null
    var preSession: WIFISession = null
    var curSession: WIFISession = null

    /*
     * Use algorithm iterated from previous GWJ's version of SyslogCleanser project.
     */
    logs.foreach( log => {
      /*
       * construct network sessions roughly
       * currently, we end a session when AUTH and DEAUTH pair is detected
       */
      val mac = log.MAC
      val time = log.time
      val code = log.code
      val ap = log.payload

      if ( code == WIFICodeSchema.AuthRequest || code == WIFICodeSchema.AssocRequest) {

        if ( ! APMap.contains(ap) || (APMap.contains(ap) && ap != preAP))
          APMap.put(ap, time)

      } else if (code == WIFICodeSchema.Deauth || code == WIFICodeSchema.Disassoc) {

        if ( APMap.contains(ap) ) {
          // record this new session and remove it from APMap
          val stime = APMap.get(ap).get
          curSession = WIFISession(mac, stime, time, ap)
          APMap.remove(ap)

          // adjust session timestamps
          if ( preSession != null ) {
            val tdiff = curSession.stime - preSession.etime
            if (tdiff < 0)
              preSession = preSession.copy(etime = curSession.stime)

            // merge adjacent sessions under the same AP
            if ( preSession.AP == curSession.AP && tdiff < mergeSessionThreshold )
              preSession = preSession.copy(etime = curSession.etime)
            else {
              sessions = sessions :+ preSession
              preSession = curSession
            }
          } else {
            preSession = curSession
          }
        }
      }
      preAP = ap
    })

    if (preSession != null)
      sessions = sessions :+ preSession

    sessions.toIterable
  }

  /**
   * Construct IP sessions identified by IPALLOC and IPRECYCLE messages
   * @param logs
   * @return
   */
  def collectIPSession(logs: Iterable[CleanWIFILog]): Iterable[IPSession] = {
    var sessions = new Array[IPSession](0)
    var IPMap = new HashMap[String, List[Long]]
    var mac: String = null

    logs.foreach( log => {
      mac = log.MAC
      val time = log.time
      val code = log.code
      val ip = log.payload

      if ( code == WIFICodeSchema.IPAllocation ) {

        if ( ! IPMap.contains(ip) )
          IPMap.put(ip, List(time, time))
        else {
          val value = IPMap.get(ip).get
          if ( time >= value(1) ) {
            // update session ending time
            IPMap.put(ip, List(value(0), time))
          }
        }

      } else if (code == WIFICodeSchema.IPRecycle) {

        if ( IPMap.contains(ip)) {
          val value = IPMap.get(ip).get
          // recycle certain IP
          sessions = sessions :+ IPSession(mac, value(0), time, ip)
          IPMap.remove(ip)
        } else {
          // omit recycling messages without allocation first
        }

      }
    })

    if ( mac != null ){
      IPMap.foreach { case (key, value) => {
        sessions = sessions :+ IPSession(mac, value(0), value(1), key)
      }}
    }

    // adjust session timestamps
    var preSession: IPSession = null
    var ajustedSessions = new Array[IPSession](0)
    sessions.sortBy(m => m.stime).foreach { m => {

      if ( preSession != null ) {
        val tdiff = m.stime - m.etime
        if (tdiff < 0)
          preSession = preSession.copy(etime = m.stime)

        // merge adjacent sessions with the same IP
        if ( preSession.IP == m.IP && tdiff < mergeSessionThreshold )
          preSession = preSession.copy(etime = m.etime)
        else {
          ajustedSessions = ajustedSessions :+ preSession
          preSession = m
        }
      } else {
        preSession = m
      }

    }}

    if (preSession != null)
      ajustedSessions = ajustedSessions :+ preSession

    ajustedSessions.toIterable
  }

}
