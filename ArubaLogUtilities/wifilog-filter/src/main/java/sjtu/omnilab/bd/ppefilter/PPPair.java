package sjtu.omnilab.bd.ppefilter;

/**
 * Created by chenxm on 11/3/14.
 */
public class PPPair{
    /*
     * A ping-pong pair consists of two AP records.
     * The first can be any record of the AP sequence and the other
     * be the nearest record of the same AP after it.
     * Here, we define dist(pair) <= 3.
     * E.g., for AP sequence {A B C A D E C} we only get AP pair
     * p(0,3) for "A".
     */
    public int offset;		// offset to the head of AP sequence.
    public int distance;	// distance between the head and tail of AP pair


    public PPPair(int offset, int distance){
        this.offset = offset;
        this.distance = distance;
    }


    public int coverage(PPPair p){
		/*
		 * c(.) is the function to calculate the coverage of two AP pairs.
		 * Here we define c(.) as dist(i) - |offset(i) - offset(j)| where i < j;
		 */
        return (this.offset < p.offset ? this.distance : p.distance) - Math.abs(this.offset - p.offset);
    }
}
