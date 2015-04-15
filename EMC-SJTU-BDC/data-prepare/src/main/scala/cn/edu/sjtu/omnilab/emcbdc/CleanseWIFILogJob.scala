package cn.edu.sjtu.omnilab.emcbdc

import org.apache.spark.rdd.RDD
import org.apache.spark.storage.StorageLevel
import org.apache.spark._
import org.apache.spark.SparkContext._

import scala.collection.mutable.HashMap

case class CleanWIFILog(MAC: String, time: Long, code: Int, AP: String, account: String, IP: String)
case class IPSession(MAC: String, stime: Long, etime: Long, IP: String)
case class WIFISession(MAC: String, stime: Long, etime: Long, AP: String, IP: String, account: String)

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
 * Cleanse WIFI movement log for EMCBDC;
 * Generate movement sessions with JAccount association.
 *
 * The same result with `CombineMovAccJob.scala`
 */
object CleanseWIFILogJob {

  final val ap2build = new APToBuilding()
  final val mergeSessionThreshold: Long = 10 * 1000
  final val IPSessionTimeShift: Long = 5 * 60 * 1000

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
          val mac = parts(0)
          val time = Utils.ISOToUnix(parts(1))
          val code = parts(2).toInt
          val payload = parts(3)

          if ( code == WIFICodeSchema.UserAuth ) {
            cleanLog = try {
              val IP = parts(4)
              CleanWIFILog(mac, time, code, null, payload, IP)
            } catch {
              case e: Exception =>
                CleanWIFILog(mac, time, code, null, payload, "0.0.0.0")
            }
          } else if ( code == WIFICodeSchema.IPAllocation || code == WIFICodeSchema.IPRecycle) {
            cleanLog = CleanWIFILog(mac, time, code, null, null, payload)
          } else {
            val building = try {
              ap2build.parse(payload).get(0)
            } catch {
              case e: Exception => null
            }

            cleanLog = CleanWIFILog(mac, time, code, building, null, null)
          }
        }
        cleanLog

      }}.filter(_ != null).persist(StorageLevel.MEMORY_AND_DISK_SER)

    // extract WIFI association sessions
    val validSessionCodes = List(
      WIFICodeSchema.AuthRequest,
      WIFICodeSchema.AssocRequest,
      WIFICodeSchema.Deauth,
      WIFICodeSchema.Disassoc )

    val WIFIRDD = inRDD
      .filter(m => validSessionCodes.contains(m.code))
      .sortBy(_.time)
      .groupBy(_.MAC)
      .flatMap { case (key, logs) => { extractSessions(logs) }}
      .persist(StorageLevel.MEMORY_AND_DISK_SER)

    // extract IP allocation sessions
    val IPRDD = inRDD
      .filter( m => m.code == WIFICodeSchema.IPAllocation || m.code == WIFICodeSchema.IPRecycle)
      .groupBy(_.MAC)
      .flatMap { case (key, logs) => { collectIPSession(logs) }}
      .persist(StorageLevel.MEMORY_AND_DISK_SER)

    // filter user authentication messages
    val authRDD = inRDD.filter(m => m.code == WIFICodeSchema.UserAuth)
      .distinct
      .persist(StorageLevel.MEMORY_AND_DISK_SER)

    // add IP and account info onto WIFI sessions
    val mergedIP = combineWIFIAndIP(WIFIRDD, IPRDD)
    val mergedSession = combineWIFIAndAcc(mergedIP, authRDD)
      .sortBy(m => (m.MAC, m.stime))

    mergedSession.map { m =>
      "%s,%d,%d,%s,%s,%s".format(m.MAC, m.stime, m.etime, m.AP, m.IP, m.account)
    }.saveAsTextFile(output)

    spark.stop()

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
      val ap = log.AP

      if ( code == WIFICodeSchema.AuthRequest || code == WIFICodeSchema.AssocRequest) {

        if ( ! APMap.contains(ap) || (APMap.contains(ap) && ap != preAP))
          APMap.put(ap, time)

      } else if (code == WIFICodeSchema.Deauth || code == WIFICodeSchema.Disassoc) {

        if ( APMap.contains(ap) ) {
          // record this new session and remove it from APMap
          val stime = APMap.get(ap).get
          curSession = WIFISession(mac, stime, time, ap, null, null)
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
      val ip = log.IP

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

  /**
   * Combine WIFI sessions and IP sessions:
   *
   * Adding an IP address to individual WIFI sessions.
   * Adding null if there is no corresponding IP address.
   *
   * @param WIFIRDD
   * @param IPRDD
   * @return
   */
  def combineWIFIAndIP(WIFIRDD: RDD[WIFISession], IPRDD: RDD[IPSession]): RDD[WIFISession] = {

    val keyedIP = IPRDD.keyBy(m => (m.MAC, m.stime / 1000 / 3600 / 24))
      .groupByKey.persist(StorageLevel.MEMORY_AND_DISK_SER)

    WIFIRDD.keyBy(m => (m.MAC, m.stime / 1000 / 3600 / 24))
      .groupByKey
      .leftOuterJoin(keyedIP)
      .flatMap {
        case (key, (wifisession, ipsession)) => {

          val orderdIP = try {
            ipsession.get.toArray.sortBy(- _.stime) // revservely
          } catch {
            case e: Exception => new Array[IPSession](0)
          }

          // add IP to certain WIFI session
          // TODO: this can be optimized
          var results = new Array[WIFISession](0)

          wifisession.foreach( mov => {
            var IPFound: IPSession = null

            // exact match
            orderdIP.foreach { ip => {
              if (IPFound == null && (
                  ip.stime >= mov.stime && ip.stime <= mov.etime ||
                  mov.stime >= ip.stime && mov.stime <= ip.etime
                ))
                IPFound = ip
            }}

            // fuzzy match: considering time shift of servers
            if ( IPFound == null ) {
              orderdIP.foreach { ip => {
                val ipstime = ip.stime - IPSessionTimeShift
                val ipetime = ip.etime + IPSessionTimeShift

                if (ipstime >= mov.stime && ipstime <= mov.etime ||
                    mov.stime >= ipstime && mov.stime <= ipetime)
                  IPFound = ip
              }}
            }

            var IP: String = null
            if ( IPFound != null ) IP = IPFound.IP

            results = results :+ mov.copy(IP=IP)
          })

          results
      }}
  }

  /**
   * Combine WIFI sessions and user account info, i.e.
   * adding an account to individual WIFI sessions.
   * @param WIFIRDD
   * @param ACCRDD
   * @return
   */
  def combineWIFIAndAcc(WIFIRDD: RDD[WIFISession], ACCRDD: RDD[CleanWIFILog]): RDD[WIFISession] = {
    val keyedWIFI = WIFIRDD.keyBy(m => (m.MAC, m.stime/1000/3600/24))
    val keyedAuth = ACCRDD.keyBy(m => (m.MAC, m.time/1000/3600/24)).distinct

    // join movement and accounts by (MAC, day),
    keyedWIFI.leftOuterJoin(keyedAuth).filter {
      case (key, (mov, account)) => {
        val acc = account.getOrElse(null)
        // filter out the combinations without valid IP connection
        if ( acc != null && acc.IP != null && acc.IP != "0.0.0.0" && mov.IP != acc.IP) false
        else true
      }
    }.map {
      case (key, (mov, account)) => {
        val acc = try {
          account.get.account
        } catch {
          case e: Exception => null
        }

        mov.copy(mov.MAC, mov.stime, mov.etime, mov.AP, mov.IP, acc)
      }
    }.distinct
  }
}
