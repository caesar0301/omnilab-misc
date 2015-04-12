package cn.edu.sjtu.omnilab.emcbdc

import org.apache.spark.{SparkContext, SparkConf}
import org.apache.spark.SparkContext._


/**
 * Combine WIFI movement and traffic logs
 */
object CombineMovLogJob {

  // time tolerance to determine user location within a WIFI session
  final val SessionExt = 5 * 60 * 1000

  def main(args: Array[String]): Unit = {

    if ( args.length != 3 ) {
      println("Usage: CombineMovLogJob <wifilog.in> <wifimov.in> <out>")
      sys.exit(-1)
    }

    val wifilog = args(0)
    val wifimov = args(1)
    val output = args(2)

    val conf = new SparkConf()
    conf.setAppName("Combine traffic and movement data for EMCBDC")
    val spark = new SparkContext(conf)

    val wifilogRDD = spark.textFile(wifilog).map { m => {
      val parts = m.split(',')
      SessionStat(IP=parts(0), stime=parts(1).toLong,
        sdur=parts(2).toLong, mobile=parts(3),
        sps=parts(4), bytes=parts(5), requests=parts(6))
    }}

    val wifimovRDD = spark.textFile(wifimov).map { m => {
      val parts = m.split(',')
      Movement(MAC=parts(0), stime=parts(1).toLong,
        etime=parts(2).toLong, building=parts(3),
        IP=parts(4), account=parts(5))
    }}

    val keyedLog = wifilogRDD.keyBy(m => (m.IP, m.stime/1000/3600/24))
    val keyedMov = wifimovRDD.keyBy(m => (m.IP, m.stime/1000/3600/24))

    val joined = keyedLog.join(keyedMov).filter {
      case (key, (session, mov)) => {
        val stime_ex = mov.stime - SessionExt
        val etime_ex = mov.etime + SessionExt
        session.stime >= stime_ex && session.stime <= etime_ex
      }}.map( _._2)

    joined.saveAsTextFile(output)
  }

}
