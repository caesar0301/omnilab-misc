package cn.edu.sjtu.omnilab.emcbdc

import java.util.UUID

import org.apache.spark._
import org.apache.spark.SparkContext._
import org.apache.spark.storage.StorageLevel
import org.joda.time.DateTime

case class CleanLog(IP: String, stime: Long, etime: Long,
                    size: Long, mobile: String, SP: String,
                    SCAT: String, host: String, SID: String)

case class ContextLog(IP: String, stime: Long, etime: Long,
                      size: Long, mobile: String, SP: String,
                      SCAT: String, host: String, location: String,
                      account: String, SID: String)

case class ContextSession(account: String, stime: Long, sdur: Long,
                          mobile: String, sps: String, scats: String, hosts: String,
                          bytes: String, requests: String, location: String)

/**
 * A Spark job to cleanse SJTU HTTP logs for EMC Big Data Challenge (EMCBDC).
 *
 * Two datasets are required to generate the final version:
 * Clean WIFI traffic log and jaccount-marked movement sessions.
 *
 * Return the contextual session stat.
 *
 * @author: Xiaming Chen, chenxm35@gmail.com
 */
object PrepareDataJob {

  final val serviceClassifier = new ServiceCategoryClassify()
  final val sessionGapMinutes = 5
  final val movementToleranceMinutes = 5

  def main( args: Array[String] ): Unit = {

    // parse command options
    if (args.length < 3){
      println("Usage: PrepareDataJob <HTTPLOG> <MOVDAT> <CLEANOUT>")
      sys.exit(0)
    }

    val wifilog = args(0)
    val movdat = args(1)
    val output = args(2)

    // configure spark
    val conf = new SparkConf()
      .setAppName("Data preparation for EMCBDC")
    val spark = new SparkContext(conf)

    // extract fields from raw logs and validate input data
    val cleanRDD = spark.textFile(wifilog)
      .map( m => transformFieldsForBDC(cleanseLog(m)) )
      .filter(t => t != null && t.SP != null)

    // split the whole data into subsets by months
//    val wholeRDD = cleanRDD.keyBy(m => getFileName(m.stime))
//      .mapValues { m =>
//      "%s,%d,%d,%d,%s,%s,%s,%s,%s".format(m.IP, m.stime, m.etime, m.size,
//        m.mobile, m.SP, m.SCAT, m.host, m.SID)
//    }.partitionBy(new HashPartitioner(32))
//      .saveAsHadoopFile(output, classOf[String], classOf[String],
//        classOf[RDDMultipleTextOutputFormat])

    // load movement data
    val movRDD = spark.textFile(movdat).map { m => {
      val parts = m.split(',')
      WIFISession(parts(0), parts(1).toLong, parts(2).toLong, parts(3), parts(4), parts(5))
    }}.keyBy(m => (m.IP, m.stime / 1000 / 3600 / 24))
      .groupByKey().persist(StorageLevel.MEMORY_AND_DISK_SER)

    // join wifi traffic and movement data
    val joinedRDD = cleanRDD
      .keyBy(m => (m.IP, m.stime / 1000 / 3600 / 24))
      .groupByKey.join(movRDD)
      .flatMap { case (key, (logs, movs)) => {

        val ordered = movs.toArray.sortBy(_.stime)

        // find the movement session that contains given HTTP log
        // TODO: this can be optimized
        var mergedLogs = new Array[ContextLog](0)
        logs.foreach { m => {

          var movFound: WIFISession = null
          // exact match
          ordered.foreach { mov => {
            if ( movFound == null && m.stime >= mov.stime && m.stime <= mov.etime )
              movFound = mov
          }}

          if ( movFound == null ) {
            // fuzzy match
            ordered.foreach { mov => {
              val stime_ex = mov.stime - movementToleranceMinutes * 60 * 1000
              val etime_ex = mov.etime + movementToleranceMinutes * 60 * 1000

              if ( movFound == null && m.stime >= stime_ex && m.stime <= etime_ex )
                movFound = mov
            }}
          }

          var clog: ContextLog = null
          if ( movFound != null ) {
            // create new contextual log
            mergedLogs = mergedLogs :+ ContextLog(
              IP = m.IP, stime = m.stime, etime = m.etime, size = m.size,
              mobile = m.mobile, SP = m.SP, SCAT = m.SCAT,
              host = Utils.getTopPrivateDomain(m.host),
              location = movFound.AP,
              account = movFound.account, SID = null)
          }

        }}

        mergedLogs.toIterable

    }}.persist(StorageLevel.MEMORY_AND_DISK_SER)

    // extract session stat
    val sessions = joinedRDD.groupBy( m => {
      (m.account, m.stime / 1000 / 3600 / 24)
    }).flatMap { case (key, iter) => markContextSessions(iter) }
      .groupBy(_.SID)
      .map { case (sid, iter) => extractSessionStat(iter)}

    sessions.sortBy(m => (m.account, m.stime)).map(m => {
      "%s\t%s\t%d\t%d\t%s\t%s\t%s\t%s\t%s\t%s".format(
        m.account, m.location, m.stime, m.sdur, m.mobile,
        m.sps, m.scats, m.hosts, m.bytes, m.requests)
    }).saveAsTextFile(output)

    spark.stop()

  }

  /**
   * Parse date value as file name from recording time.
   * @param milliSecond
   * @return
   */
  def getFileName(milliSecond: Long): String = {
    val datetime = new DateTime(milliSecond)
    return "SET%02d%02d".format(datetime.getYearOfCentury, datetime.getMonthOfYear)
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
    // filter out invalid messages for this BDC
    if ( line == null || line(DataSchema.source_port) == null ||
      line(DataSchema.request_ts) == null || line(DataSchema.request_size) == null ||
      line(DataSchema.request_host) == null )
      return null

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
  def markContextSessions(records: Iterable[ContextLog]): Iterable[ContextLog] = {
    var curUUID = UUID.randomUUID.toString
    var lastTimestamp: Long = -1
    var lastLocation: String = null

    records.toArray.sortBy(_.stime).transform( m => {
      val curTimestamp = m.stime
      val curLocation = m.location

      if ( lastTimestamp < 0 || curTimestamp - lastTimestamp > sessionGapMinutes * 60 * 1000) {
        curUUID = UUID.randomUUID.toString // update UUID for a new session
      } else if ( curLocation != lastLocation )
        curUUID = UUID.randomUUID.toString

      lastLocation = curLocation
      lastTimestamp = curTimestamp
      m.copy( SID = curUUID)
    }).toIterable
  }

  /**
   * Compress user activities into sessions and calculate session metrics
   * @param iter
   * @return
   */
  def extractSessionStat(iter: Iterable[ContextLog]): ContextSession = {
    val records = iter.toArray.sortBy(_.stime)
    val id = records(0).account
    val location = records(0).location
    val stime = records.map(_.stime).min
    val sdur = records.map(_.etime).max - stime

    // get the toppest mobile client type which is not "unknown"
    val mobileCount = records.map(_.mobile).groupBy(identity)
      .mapValues(_.size).filterKeys(_ != "unknown")
    var mobile: String = null
    if (mobileCount.size > 0)
      mobile = mobileCount.maxBy(_._2)._1

    // calculate transmission stat for different service provider
    val serviceGroup = records.groupBy(x => (x.SP, x.SCAT, x.host))
      .mapValues(m => {
        val bytes = m.map(_.size).sum
        val requests = m.length
        (bytes, requests)
      })

    val ordered = serviceGroup.toSeq.sortBy(- _._2._1) // order by bytes, reversely

    // all applications
    val sps = ordered.map(_._1._1).mkString(";")
    val scats = ordered.map(_._1._2).mkString(";")
    val hosts = ordered.map(_._1._3).mkString(";")
    val bytes = ordered.map(_._2._1).mkString(";")
    val requests = ordered.map(_._2._2).mkString(";")

    // only TOP 1 application
//    val top1 = ordered(0)
//    val sps = top1._1._1
//    val scats = top1._1._2
//    val hosts = top1._1._3
//    val bytes = ordered.map(_._2._1).sum.toString
//    val requests = ordered.map(_._2._2).sum.toString

    ContextSession(account=id, stime=stime, sdur=sdur, mobile=mobile,
      bytes=bytes, requests=requests, sps=sps, scats=scats, hosts=hosts,
      location=location)
  }
}
