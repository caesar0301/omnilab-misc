package sjtu.omnilab.bd.ppefilter;

/**
 * Created by chenxm on 11/3/14.
 */
public class DataPoint {
    public int i;	// mask length - 3
    public int j;	// start
    public int pair_count;
    public int item_undup;
    public int item_total;
    public int distance;
    public int max_distance;
    public DataPoint(int i, int j){
        this.i = i;
        this.j = j;
    }
    public double measure() {
		/*
		 * Measure the closeness of PingPong records
		 */
        double score = -1.0;
        if ( distance != 0) {
            score = Math.pow(pair_count, 2) / (double) distance * (1 - (double)item_undup / item_total);
            if (score == Double.POSITIVE_INFINITY){
                score = -1.0;
            }
        }
        return score;
    }
    public int start_index(){
        return j;
    }
    public int stop_index(){
        return j+i+2;
    }
    public int mask_length(){
        return i+3;
    }
}
