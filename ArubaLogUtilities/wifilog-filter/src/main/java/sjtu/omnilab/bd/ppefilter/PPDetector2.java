package sjtu.omnilab.bd.ppefilter;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class PPDetector2 {
	
	public PPDetector2(){}
	
	
	public static List<APRecord> removePingPong (
			List<String> tmp_ap_list, List<Long> tmp_start_times, 
			List<Long> tmp_durations, List<Boolean> tmp_flags)
			/*
			 * @Param: tmp_ap_list: sequence of APs with potential ping-pong
			 * @Param: tmp_start_times: sequence of AP session starting time aligned to AP list
			 * @Param: tmp_durations: sequence of AP durations aligned to AP list
			 * @Param: tmp_flags: sequence of AP flags that indicate to accumulate the AP duration or not.
			 */
	{
		List<String> ap_list = tmp_ap_list;
		List<Long> ap_start_time_list = tmp_start_times;
		List<Long> ap_duration_list = tmp_durations;
		List<Boolean> ap_flag_list = tmp_flags;
		int ap_count = ap_duration_list.size();
		
		if ( DebugFlag.debug ){
			System.out.println("\nPing-pong len: " + ap_count);
			for (int i=0; i<ap_count; i++) {
				System.out.println(ap_list.get(i)+"\t"+ap_duration_list.get(i)+"\t"+ap_flag_list.get(i));
			}
		}
		
		List<APRecord> filtered_records = new ArrayList<APRecord>();
		List<PPPair> pp_pairs_list = new ArrayList<PPPair>();
		
		if ( ap_count >= 3) {
			// Only sequence of longer than 3 are processed...
			// Step 1: find ping-pong pairs of AP sequence
			for ( int i = 0; i< ap_count; i++) {
				for ( int j = i+1; j< ap_count; j++) {
					if ( ap_list.get(j).equals(ap_list.get(i))) {
						if ( j-i < 4) {
							pp_pairs_list.add(new PPPair(i, j-i));
						}
						break;
					} else if ( j-i >= 4) {
						break;
					}
				}
			}
			
			if (DebugFlag.debug) {
				System.out.println("\nPing-pong pairs:");
				for ( PPPair pair : pp_pairs_list){
					System.out.println(pair.offset+","+(pair.offset+pair.distance)+" ");
				}
			}
			
			// Step 2: merge several ping-pong pairs into ping-pong segment
			/*
			 * For AP pair set {Pi | i > 0}, we define a valid ping-pong segment as:
			 * for any AP pair Pi, there is at least one Pj to make c(Pi, Pj) > 0, where
			 * c(.) is the function to calculate the coverage of two AP pairs.
			 * Here we define c(.) as dist(i) - |offset(i) - offset(j)| where i < j;
			 */
			List<List<PPPair>> pp_segment_list = new ArrayList<List<PPPair>>();
			for ( PPPair candPair : pp_pairs_list){
				boolean found = false;
				for ( List<PPPair> pp_segment : pp_segment_list) {
					for ( PPPair pp_pair: pp_segment ) {
						if ( candPair.coverage(pp_pair) > 0) {
							found = true;
							break;
						}
					}
					
					if ( found == true) {
						pp_segment.add(candPair);
						break;
					}
				}
				
				if ( found == false) {
					List<PPPair> new_segment = new ArrayList<PPPair>();
					new_segment.add(candPair);
					pp_segment_list.add(new_segment);
				}
			}
			
			
			// Step 3: construct new AP sequence from ping-pong segments
			List<PPPair> ppps = new ArrayList<PPPair>();
			for ( List<PPPair> segment : pp_segment_list){
				int new_head = ap_count+1;
				int new_tail = 0;
				for ( PPPair ppp : segment ) {
					new_head = (ppp.offset < new_head) ? ppp.offset : new_head;
					new_tail = ppp.offset+ppp.distance > new_tail ? ppp.offset+ppp.distance : new_tail;
				}
				ppps.add(new PPPair(new_head, new_tail-new_head));
			}
			
			if (DebugFlag.debug) {
				System.out.println("\nMerged ping-pong segments:");
				for ( PPPair pair : ppps){
					System.out.println(pair.offset+","+(pair.offset+pair.distance)+" ");
				}
			}

			for ( PPPair pair : ppps ){
				String fap_name = "";
				
				//****************************************
				// To generate final AP name as concatenating
				// all present APs
				Set<String> fap_name_set = new HashSet<String>();
				//****************************************
				
				//****************************************
				// To generate final AP name as the AP with 
				// longest duration
//				Map<String, Long> fap_name_map = new HashMap();
				//****************************************
				
				// start time
				long fap_start_time = -1;
				// duration
				long fap_duration = 0;
				
				for ( int i = pair.offset; i<=pair.offset + pair.distance; i++) {
					// NOTE: we accumulate the durations from start to stop and without the
					// stop, to avoid the repeated addition of the item when two segments
					// have the covered number (==1)
					
					String ap_name = ap_list.get(i);
					boolean ap_flag = ap_flag_list.get(i);
					long ap_start_time = ap_start_time_list.get(i);
					long ap_duration = ap_duration_list.get(i);
					
					//****************************************
					// To generate final AP name as concatenating
					// all present APs
					fap_name_set.add(ap_name);
					//****************************************
					
					//****************************************
					// To generate final AP name as the AP with 
					// longest duration.
					// Accumulate duration time for each AP
//					if ( fap_name_map.containsKey(ap_name) ){
//						fap_name_map.put(ap_name, fap_name_map.get(ap_name) + ap_duration);
//					} else {
//						fap_name_map.put(ap_name, ap_duration);
//					}
					//****************************************

					
					// Update Ping-ping start time
					if ( fap_start_time == -1 && ap_flag == true )
						fap_start_time = ap_start_time;
					
					// Update flags
					if ( ap_flag == true){	
						fap_duration += ap_duration;
						ap_flag_list.set(i, false);
					}
				}
				
				
				//****************************************
				// To generate final AP name as concatenating
				// all present APs
				for ( String s : fap_name_set) {
					if ( fap_name.equals(""))
						fap_name += s;
					else
						fap_name += (","+s);
				}
				//****************************************
				
				
				//****************************************
				// To generate final AP name as the AP with 
				// longest duration.
				// Accumulate duration time for each AP
//				long longest_duration = -1;
//				for ( String ap : fap_name_map.keySet()) {
//					if ( fap_name_map.get(ap) >= longest_duration ){
//						fap_name = ap;
//						longest_duration = fap_name_map.get(ap);
//					}
//				}
				//****************************************
				
				// Add this new record
				filtered_records.add(new APRecord(fap_name, fap_start_time, fap_duration));
				if (DebugFlag.debug){
					System.out.println("Merged result:");
					System.out.println(fap_name+"\t"+fap_start_time+"\t"+fap_duration);
				}
			}
		}
		
		// Add the left records which are not contained by the ping-pong segments
		for ( int j=0; j<ap_flag_list.size(); j++)
			if ( ap_flag_list.get(j) == true)
				filtered_records.add(new APRecord(ap_list.get(j), ap_start_time_list.get(j), ap_duration_list.get(j)));
		
		// Order the records by start_time
		Collections.sort(filtered_records,new Comparator<APRecord>(){
	           public int compare(APRecord arg0, APRecord arg1) {
	               return new Long(arg0.start_time).compareTo(new Long(arg1.start_time));   
	            }   
	        }); 
		
		return filtered_records;
	}
}
