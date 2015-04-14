package cn.edu.sjtu.omnilab.emcbdc

import org.apache.spark.{SparkContext, SparkConf}
import org.apache.spark.SparkContext._ // to use join etc.

case class Account(MAC: String, time: Long, account: String, IP: String)
case class Movement(MAC: String, stime: Long, etime: Long, building: String, IP: String, account: String)

/**
 * Combine WIFI movement and AUTH account info.
 */
object CombineMovAccJob {

  val ap2build = new APToBuilding()

  def main(args: Array[String]): Unit = {
    if ( args.length != 3 ) {
      println("Usage: CombineMovAccJob <wifimov.in> <wifiacc.in> <out>")
      sys.exit(-1)
    }

    val wifimov = args(0)
    val wifiacc = args(1)
    val output = args(2)

    val conf = new SparkConf()
    conf.setAppName("Combine WIFI movement and accounts for EMCBDC")
    val spark = new SparkContext(conf)

    val wifimovRDD = spark.textFile(wifimov).map(formatMovLog(_))
      .keyBy(m => (m.MAC, m.stime/1000/3600/24))

    val wifiaccRDD = spark.textFile(wifiacc).map(formatAccLog(_))
      .map ( m => m.copy(MAC=m.MAC, time=m.time/1000/3600/24, account=m.account, IP=m.IP))
      .keyBy(m => (m.MAC, m.time))
      .distinct

    // join movement and accounts by (MAC, day),
    // filter out the combinations without valid IP connection
    val joined = wifimovRDD.join(wifiaccRDD).filter {
      case (key, (mov, acc)) => {
        if ( acc.IP != null && acc.IP != "0.0.0.0" && mov.IP != acc.IP) false
        else true
      }
    }.map {
      case (key, (mov, acc)) => {
        (mov.MAC, mov.stime, mov.etime, mov.building, mov.IP, acc.account)
      }
    }.distinct.sortBy(m => (m._1, m._2))
//      .keyBy(m => (m._1, m._2, m._3, m._6)) // perform `distinct` alternative
//      .groupByKey()
//      .map { case (key, values) => values.toArray.apply(0) }
//      .sortBy(m => (m._1, m._2))

    joined.map(m => {
      "%s,%d,%d,%s,%s,%s".format(m._1, m._2, m._3, m._4, m._5, m._6)
    }).saveAsTextFile(output)

    spark.stop()
  }

  /**
   * Parse and format WIFI movement log
   * @param line
   * @return
   */
  def formatMovLog(line: String): Movement = {
    val parts = line.split('\t')
    if ( parts.length < 6)
      return null

    val mac = parts(0)
    val stime = Utils.ISOToUnix(parts(1)) // milliseconds
    val etime = Utils.ISOToUnix(parts(2))
    val buildInfo = ap2build.parse(parts(4))
    var building: String = null
    if (buildInfo != null)
      building = buildInfo.get(0)
    val IP = parts(5)

    Movement(MAC=mac, stime=stime, etime=etime, building=building, IP=IP, account=null)
  }

  /**
   * Parse and format WIFI account log
   * @param line
   * @return
   */
  def formatAccLog(line: String): Account = {
    val parts = line.split('\t')
    var hasIP = false

    if ( parts.length < 3)
      return null
    else if (parts.length >= 4)
      hasIP = true

    val mac = parts(0)
    val time = Utils.ISOToUnix(parts(1))
    val account = parts(2)
    var IP: String = null
    if (hasIP)
      IP = parts(3)

    Account(MAC=mac, time=time, account=account, IP=IP)
  }
}
