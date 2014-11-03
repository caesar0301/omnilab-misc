package sjtu.omnilab.bd.ppefilter;

/**
 * Created by chenxm on 11/3/14.
 */
public class APRecord {
    public String name;
    public long start_time;
    public long duration;
    public APRecord(String name, long start_time, long duration){
        this.name = name;
        this.start_time = start_time;
        this.duration = duration;
    }
}