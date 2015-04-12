package cn.edu.sjtu.omnilab.emcbdc

import java.util.UUID

import org.apache.spark.SparkConf
import org.apache.spark.SparkContext

case class CleanLog(IP: String, stime: Long, etime: Long,
                    size: Long, mobile: String, SP: String,
                    SCAT: String, host: String, SID: String)

case class SessionStat(IP: String, stime: Long, sdur: Long, mobile: String,
                       sps: String, bytes: String, requests: String)

/**
 * A Spark job to cleanse SJTU HTTP logs for EMCBDC.
 * @author: Xiaming Chen
 *         chenxm35@gmail.com
 */
object PrepareDataJob {

  final val serviceClassifier = new ServiceCategoryClassify()
  final val sessionGapMinutes = 10

  def main( args: Array[String] ): Unit = {

    // parse command options
    if (args.length != 2){
      println("Usage: PrepareDataJob <HTTPLOG> <CLEANOUT>")
      sys.exit(0)
    }

    val input = args(0)
    val output = args(1)

    // configure spark
    val conf = new SparkConf()
    conf.setAppName("Data cleansing for EMCBDC")
    val spark = new SparkContext(conf)

    // extract fields from logs and valid input data
    val inputRDD = spark.textFile(input)
      .map( cleanseLog(_) )
      .filter ( line => line != null &&
        line(DataSchema.source_port) != null &&
        line(DataSchema.request_ts) != null &&
        line(DataSchema.request_size) != null &&
        line(DataSchema.request_host) != null)

    // transform raw logs into clean format
    val selectedRDD = inputRDD.map(transformFieldsForBDC(_))
      // remove logs without service info
      .filter(t => t != null && t.SP != null)

    // extract session stat
    val sessions = selectedRDD.groupBy( m => {
      (m.IP, m.stime / 1000 / 3600 / 24)
    }).flatMap { case (key, iter) => markSessions(iter) }
      .groupBy(_.SID)
      .map { case (sid, iter) => extractSessionStat(iter)}

    sessions.map(m => {
      "%s,%d,%d,%s,%s,%s,%s".format(m.IP, m.stime, m.sdur, m.mobile,
        m.sps, m.bytes, m.requests)
    }).saveAsTextFile(output)

  }

  /**
   * Split individual log entry into fields
   * @param line a single entry of HTTP log
   * @return an array of separated parts
   */
  def cleanseLog(line: String): Array[String] = {
    // get HTTP header fields
    val chops = line.split("""\"\s\"""");
    if ( chops.length != 21 )
      return null

    // get timestamps
    val timestamps = chops(0).split(" ");
    if (timestamps.length != 18 )
      return null

    val results = timestamps ++ chops.slice(1, 21)

    // remove N/A values and extrat quote
    results.transform( field => {
      var new_field = field.replaceAll("\"", "")
      if (new_field == "N/A")
        new_field = null
      new_field
    })

    results
  }

  /**
   * Select data fields for EMC big data challenge
   * @param line
   * @return
   */
  def transformFieldsForBDC(line: Array[String]): CleanLog = {
    val source_ip = line(DataSchema.source_ip)

    // parse request starting time
    val request_ts = Utils.parseDouble(line(DataSchema.request_ts), -1)
    if (request_ts == -1)
      return null
    val stime = (request_ts * 1000).toLong // milliseconds

    // parse response ending time, allowing entries without responses
    val response_ts = Utils.parseDouble(line(DataSchema.response_ts), request_ts)
    val response_dur = Utils.parseDouble(line(DataSchema.response_dur_e), 0)
    val etime = ((response_ts + response_dur) * 1000).toLong

    // parse request size
    val request_size = Utils.parseLong(line(DataSchema.request_size), 0)
    val response_size = Utils.parseLong(line(DataSchema.response_size), 0)
    val size = request_size + response_size

    val host = line(DataSchema.request_host).replace("www.", "")
    // val tld = Utils.getTopPrivateDomain(host)
    // val url = Utils.stripURL(line(DataSchema.request_url))
    val mobile_type = Utils.getMobileName(line(DataSchema.request_user_agent))
    val service = serviceClassifier.parse(host).toArray()
    var service_provider: String = null
    if ( service(0) != null)
      service_provider = service(0).toString
    var service_category: String = null
    if (service(1) != null)
      service_category = service(1).toString

    // output clean log entry, without sesson key
    CleanLog(source_ip, stime, etime, size, mobile_type,
      service_provider, service_category, host, null)
  }

  /**
   * sessionize individual's logs
   * @param records
   * @return
   */
  def markSessions(records: Iterable[CleanLog]): Iterable[CleanLog] = {
    var curUUID = UUID.randomUUID.toString
    var lastTimestamp: Long = -1

    records.toArray.transform( m => {
      val curTimestamp = m.stime
      if ( lastTimestamp < 0 || curTimestamp - lastTimestamp > sessionGapMinutes * 60 * 1000) {
        curUUID = UUID.randomUUID.toString // update UUID for a new session
      }
      lastTimestamp = curTimestamp
      m.copy( SID = curUUID)
    }).toIterable
  }

  /**
   * Compress user activities into sessions and calculate session metrics
   * @param iter
   * @return
   */
  def extractSessionStat(iter: Iterable[CleanLog]): SessionStat = {
    val records = iter.toArray.sortBy(_.stime)
    val id = records(0).IP
    val stime = records.map(_.stime).min
    val sdur = records.map(_.etime).max - stime

    // get the toppest mobile client type which is not "unknown"
    val mobileCount = records.map(_.mobile).groupBy(identity)
      .mapValues(_.size).filterKeys(_ != "unknown")
    var mobile: String = null
    if (mobileCount.size > 0)
      mobile = mobileCount.maxBy(_._2)._1

    // calculate transmission stat for different service provider
    val serviceGroup = records.groupBy(x => (x.SP, x.SCAT))
      .mapValues(m => {
        val bytes = m.map(_.size).sum
        val requests = m.length
        (bytes, requests)
      })

    val sps = serviceGroup.map(_._1._1).mkString(";")
    val scats = serviceGroup.map(_._1._2).mkString(";")
    val bytes = serviceGroup.map(_._2._1).mkString(";")
    val requests = serviceGroup.map(_._2._2).mkString(";")

    SessionStat(IP=id, stime=stime, sdur=sdur, mobile=mobile,
      bytes=bytes, requests=requests, sps=sps)
  }
}
