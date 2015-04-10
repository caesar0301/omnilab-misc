package cn.edu.sjtu.omnilab.emcbdc

import org.apache.spark.SparkConf
import org.apache.spark.SparkContext

/**
 * A Spark job to cleanse SJTU HTTP logs for EMCBDC.
 */
object PrepareDataJob {

  val serviceClassifier = new ServiceCategoryClassify()

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

    // extract fields from logs and valid log entry
    val inputRDD = spark.textFile(input)
      .map( cleanseLog(_) )
      .filter ( line => line != null &&
        line(DataSchema.source_port) != null &&
        line(DataSchema.request_ts) != null &&
        line(DataSchema.request_size) != null &&
        line(DataSchema.request_host) != null)
      .cache()

    val selectedRDD = inputRDD.map(transformFieldsForBDC(_))
      .filter(_ != null)

    selectedRDD.map(_.mkString(",")).saveAsTextFile(output);

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
  def transformFieldsForBDC(line: Array[String]): Array[Any] = {
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
    val tld = Utils.getTopPrivateDomain(host)
    // val url = Utils.stripURL(line(DataSchema.request_url))
    val mobile_type = Utils.getMobileName(line(DataSchema.request_user_agent))
    val service = serviceClassifier.parse(host).toArray()
    val service_provider = service(0)
    val service_category = service(1)

    (source_ip, stime, etime, size, host, mobile_type, service_provider, service_category, tld)
      .productIterator.toArray
  }
}
