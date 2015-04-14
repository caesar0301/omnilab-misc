package cn.edu.sjtu.omnilab.emcbdc

import org.apache.spark.{SparkContext, SparkConf}
import org.apache.spark.SparkContext._ // to use join etc.

/**
 * Add JACC data onto HTTP traffic, and generate final version to public.
 */
object CombineJaccJob {

  def main(args: Array[String]): Unit = {
    if ( args.length != 3 ) {
      println("Usage: CombineJaccJob <wifilog.in> <jacc.in> <out>")
      sys.exit(-1)
    }

    val wifilog = args(0)
    val jacc = args(1)
    val output = args(2)

    val conf = new SparkConf()
    conf.setAppName("Generate final data version for EMCBDC 2015")
    val spark = new SparkContext(conf)

    val wifilogRDD = spark.textFile(wifilog)
      .keyBy(m => m.split('\t')(0)) // keyby user account

    val jacRDD = spark.textFile(jacc)
      .keyBy(m => m.split(',')(0))

    val joinedRDD = wifilogRDD.join(jacRDD)
      .map { case (key, (log, profile)) => {
      val parts = log.split('\t')
      val acc = parts(0)
      val location = parts(1)
      val stime = parts(2)
      val sdur = parts(3)
      val mobile = parts(4)
      val sp = parts(5)
      val scat = parts(6)
      val host = parts(7)
      val bytes = parts(8)
      val requests = parts(9)

      val chops = profile.split(',')
      val jacc = chops(0)
      val id = chops(1)
      val sex = chops(2)
      val birth = chops(3)
      val eduy = chops(4)

      (id, location, stime, sdur, sp, scat, host, bytes, requests, sex, birth, eduy)
    }}

    // dump user profiles
    val profileRDD = joinedRDD.map( m => (m._1, m._10, m._11, m._12))
      .distinct
      .map( _.productIterator.mkString(","))
      .saveAsTextFile(output + ".acc")

    // dump HTTP traffic
    joinedRDD.sortBy( m => (m._1, m._3))
      .map {m => m.productIterator.slice(0, 9).mkString(",") }
      .saveAsTextFile(output)

    spark.stop()
  }
}
