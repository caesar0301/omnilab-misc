package cn.edu.sjtu.omnilab.emcbdc

import org.apache.spark.{SparkConf, SparkContext}

/**
 * Cleanse WIFI movement log for EMCBDC.
 */
object CleanseWIFILogJob {

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

    val inRDD = spark.textFile(input)

    inRDD.map(WIFILogFilter.filterData(_)).filter(_ != null)
      .saveAsTextFile(output)

  }

}
