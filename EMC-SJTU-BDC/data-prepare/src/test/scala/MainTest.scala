import cn.edu.sjtu.omnilab.emcbdc.WIFILogFilter

/**
 * Created by chenxm on 4/12/15.
 */
object MainTest {

  def main(args: Array[String]): Unit = {
    val line = "1391097986162 <141>Jan 31 00:06:12 2014 10.192.28.15 stm[681]: <501106> <NOTI> |AP FH-NL-4F-04@10.192.28.15 stm|  Deauth to sta: b8:78:2e:b8:27:35: Ageout AP 10.192.28.15-6c:f3:7f:36:57:21-FH-NL-4F-04 handle_sapcp"
    println(WIFILogFilter.filterData(line))
  }

}
