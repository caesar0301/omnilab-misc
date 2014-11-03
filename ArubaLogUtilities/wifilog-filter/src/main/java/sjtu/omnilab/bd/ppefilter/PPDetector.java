package sjtu.omnilab.bd.ppefilter;

import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class PPDetector {
	/*
	 * Main class to detect Ping-Pong effect and remove it from the ap records
	 */
	private static DataPoint calculate_ppe_measure( ArrayList<String> aps, int start, int mask_len) {
		/*
		 * Calculating the PP measure for a list of given AP records.
		 */
		DataPoint dp = new DataPoint(mask_len-3, start);
		if ( start+mask_len-1 < aps.size() ) {
			// valid AP sequence
			dp.item_total = aps.size();
			Map<String, Integer> apsta = new HashMap<String, Integer>();
			for ( int k = start; k < start + mask_len; k++ ){
				String apname = aps.get(k);
				int v;
				if ( apsta.containsKey(apname))
					v  = apsta.get(apname).intValue()+1;
				else
					v = 1;
				apsta.put(apname, v);
			}
			dp.pair_count = mask_len - apsta.size();
			for ( Map.Entry<String, Integer> e : apsta.entrySet() ) {
				int first = -1;
				if ( e.getValue().intValue() == 1 )
					dp.item_undup++;
				else
					for ( int k = start; k < start+mask_len; k++ )
						if ( aps.get(k).equals(e.getKey())){
							if ( first == -1 )
								first = k;
							else {
								int pair_dist = k - first;
								if ( dp.max_distance < pair_dist )
									dp.max_distance = pair_dist;
								dp.distance += pair_dist;
								first = k;
							}
						}
			}
		}
		return dp;
	}
	
	private static boolean is_local_maxima(double[] seq, int j){
		boolean found = false;
		if ( j == 0 && seq[j] != -1 ) {
			if ( j+1>=seq.length || seq[j+1] == -1 || seq[j+1] < seq[j]){
				found = true;
			}
		} else if ( j == seq.length-1 && seq[j] != -1 ) {
			if ( j-1<0 || seq[j-1] == -1 || seq[j-1]<seq[j]) {
				found = true;
			}
		} else if ( j > 0 && j < seq.length-1) {
			if ( (seq[j-1] == -1 && seq[j+1]!=-1 && seq[j+1] < seq[j]) ||
				 (seq[j+1] == -1 && seq[j-1]!=-1 && seq[j-1] < seq[j]) ||
				 (seq[j-1]!=-1 && seq[j-1]<seq[j] && seq[j+1]!=-1 && seq[j+1]<seq[j])) {
				found = true;
			}
		}
		return found;
	}
	
	private static ArrayList<Integer> find_local_maxima(double[] seq) {
		ArrayList<Integer> max_js = new ArrayList<Integer>();
		for (int j=0; j<seq.length; j++) {
			if ( j == 0 && seq[j] != -1 ) {
				if ( j+1>=seq.length || seq[j+1] == -1 || seq[j+1] < seq[j])
					max_js.add(j);
			} else if ( j == seq.length-1 && seq[j] != -1) {
				if ( j-1<0 || seq[j-1] == -1 || seq[j-1]<seq[j])
					max_js.add(j);
			} else if ( j > 0 && j < seq.length-1) {
				if ( (seq[j-1] == -1 && seq[j+1]!=-1 && seq[j+1] < seq[j]) ||
					 (seq[j+1] == -1 && seq[j-1]!=-1 && seq[j-1] < seq[j]) ||
					 (seq[j-1]!=-1 && seq[j-1]<seq[j] && seq[j+1]!=-1 && seq[j+1]<seq[j]))
					max_js.add(j);
			}
		}
		return max_js;
	}
	
	@SuppressWarnings("unchecked")
	private static List<DataPoint> find_pp_points(DataPoint[][] ppm) {
		/*
		 * Find the optimal data points the measure matrix in three directions
		 */
		ArrayList<DataPoint> points = new ArrayList<DataPoint>();
		// Find the local maxima points
		for( int i = 0; i < ppm.length; i++) {		
			// Find the local maxima in row, col and diag directions
			// row direction
			double[] measures_row = new double[ppm[i].length];
			for ( int j=0; j<ppm[i].length; j++) {
				measures_row[j] = ppm[i][j].measure();
			}
			List<Integer> max_js = find_local_maxima(measures_row);
			for ( Integer j : max_js) {
				// col direction
				double[] measures_col = new double[ppm.length];
				// diag direction
				List<Double> measures_diagArrayList = new ArrayList<Double>();
				for ( int k = 0; k<ppm.length; k++) {
					measures_col[k] = ppm[k][j].measure();
					if (i+j-k >=0 && i+j-k < ppm[k].length)
						measures_diagArrayList.add(ppm[k][i+j-k].measure());
				}
				double[] measures_diag = new double[measures_diagArrayList.size()];
				for ( int k = 0; k<measures_diag.length; k++)
					measures_diag[k] = measures_diagArrayList.get(k).doubleValue();
				// Final decision
				if ( is_local_maxima(measures_col, i) && is_local_maxima(measures_diag, i))
					points.add(ppm[i][j]);
			}
		}
		// Reduce the local mexima set
		Set<DataPoint> removed = new HashSet<DataPoint>();
		for ( DataPoint dp1 : points)
			for ( DataPoint dp2 : points) 
				if (! removed.contains(dp1) && !removed.contains(dp2)) {
					if ( dp2.max_distance > 3) {
						removed.add(dp2);
						continue;
					}
					if ( !dp1.equals(dp2)) {
						int cover_num = 0;
						for ( int i=dp1.start_index(); i<=dp1.stop_index(); i++)
							if ( i>= dp2.start_index() && i<= dp2.stop_index())
								cover_num++;
						if ( cover_num > 1) {
							if (dp1.mask_length() < dp2.mask_length())
								removed.add(dp2);
							else if (dp1.mask_length() > dp2.mask_length()) {
								removed.add(dp1);
							} else {
								if ( dp1.start_index() <= dp2.start_index())
									removed.add(dp2);
								else
									removed.add(dp1);
							}
						}
					}
				}
		for ( DataPoint dp : (ArrayList<DataPoint>)points.clone()){
			if ( removed.contains(dp)){
				points.remove(dp);
			}
		}
		return points;
	}
	
	public static ArrayList<APRecord> RemovePP(ArrayList<String> tmp_ap_list,
			ArrayList<Long> tmp_start_times, ArrayList<Long> tmp_durations, ArrayList<Boolean> tmp_flags)
	/*
	 *  The core algorithm of filtering the Ping-Pong-Effect data points
	 */
	{
		
		System.out.println("len: " + tmp_ap_list.size());
		
		ArrayList<APRecord> filtered_records = new ArrayList<APRecord>();
		int ap_count = tmp_durations.size();
		if ( ap_count >= 3) {
			// Calculating the Ping-pong-effect measure matrix
			int m = ap_count-2;
			int n = ap_count-2;
			DataPoint[][] ppe_measure_matrix = new DataPoint[m][n];
			for ( int i = 0; i < m; i++)
				for ( int j =0; j < n; j++)
					ppe_measure_matrix[i][j] = calculate_ppe_measure(tmp_ap_list, j, i+3);
			
			if (DebugFlag.debug) {
				// Print out the measure matrix
				System.out.println("\nPPE measure matrix:");
				DecimalFormat format = new DecimalFormat("0.000");
				for ( int i = 0; i < m; i++) {
					for ( int j =0; j < n; j++)
						System.out.print(format.format(ppe_measure_matrix[i][j].measure()) + "\t");
					System.out.println();
				}
			}
			
			// Find the Ping-pong segments
			List<DataPoint> ppps = find_pp_points(ppe_measure_matrix);
			
			if ( DebugFlag.debug)
				System.out.println("\nindex(0,0)\tstart_index(0:)\tmask_length(1:)\tscore");
			
			for ( DataPoint dp : ppps ){
				
				if ( DebugFlag.debug)
					System.out.println("("+dp.i+","+dp.j+")"+"\t"+dp.start_index()+"\t"+dp.mask_length()+"\t"+dp.measure());
				
				String fap_name = "";
				Set<String> fap_name_set = new HashSet<String>();
				long fap_start_time = -1;
				long fap_duration = 0;
				for ( int i=dp.start_index(); i<=dp.stop_index(); i++) {
					// NOTE: we accumulate the durations from start to stop and without the
					// stop, to avoid the repeated addition of the item when two segments
					// have the covered number (==1)
					fap_name_set.add(tmp_ap_list.get(i));
					if ( fap_start_time == -1 && tmp_flags.get(i).booleanValue() == true )
						fap_start_time = tmp_start_times.get(i);
					if ( tmp_flags.get(i).booleanValue() == true){	
						fap_duration += tmp_durations.get(i);
						tmp_flags.set(i, false);
					}
					
				}
				for ( String s : fap_name_set) {
					if ( fap_name.equals(""))
						fap_name += s;
					else
						fap_name += (","+s);
				}
				filtered_records.add(new APRecord(fap_name, fap_start_time, fap_duration));
			}
		}
		// Add the left records which are not contained by the ping-pong segments
		for ( int j=0; j<tmp_flags.size(); j++)
			if ( tmp_flags.get(j) )
				filtered_records.add(new APRecord(tmp_ap_list.get(j), tmp_start_times.get(j), tmp_durations.get(j)));
		// Order the records by start_time
		Collections.sort(filtered_records,new Comparator<APRecord>(){
	           public int compare(APRecord arg0, APRecord arg1) {
	               return new Long(arg0.start_time).compareTo(new Long(arg1.start_time));   
	            }   
	        });  
		return filtered_records;
	}
}
