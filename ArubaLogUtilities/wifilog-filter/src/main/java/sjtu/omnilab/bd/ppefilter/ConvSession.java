package sjtu.omnilab.bd.ppefilter;

import java.util.ArrayList;
import java.util.List;

public class ConvSession {
	/*
	 * Unit of clearing AP PingPong subsequence.
	 * If the duration of a record is longer than SESSION_DURATION_WITHOUT_PPE, 
	 * it's treated as non-PPE.
	 */
	private int SESSION_DURATION_WITHOUT_PPE = 30;
	private int MAX_RECORDS_FOR_ONE_SESSION = 1000;
	private long latest_time;
	private String user_id;
	private ArrayList<String> ap_list;
	private ArrayList<Long> ap_start_times;
	private ArrayList<Long> ap_durations;
	
	public ConvSession (String uid) {
		latest_time = -1;
		user_id = uid;
		ap_list = new ArrayList<String>();
		ap_durations = new ArrayList<Long>();
		ap_start_times = new ArrayList<Long>();
	}
	
	public void addRecord(long timestamp, String apname){
		/**
	     *  Add an AP record to conversation session
	     */
		if ( ap_start_times.size() > 0) {
			ap_durations.add( new Long( timestamp - latest_time ));
		}
		ap_start_times.add(timestamp);
		ap_list.add(apname.trim());
		this.latest_time = timestamp;
	}
	
	public List<APRecord> removePingPongEffect () {
		/*
		 * Remove PingPong series from ap sequence and return 
		 * a list of ap records without PP.
		 */
		System.out.println("*****New session of user " + user_id + "*****");
		
		if (DebugFlag.debug)
		{
			// Print the original records
			int i = 0;
			for ( ; i < ap_durations.size(); i++ )
				System.out.println( ap_list.get(i) + "\t" + ap_durations.get(i));
			System.out.println(ap_list.get(i));
		}
		
		List<APRecord> final_records = new ArrayList<APRecord>();
		List<String>	tmp_ap_list = new ArrayList<String>();
		List<Long>		tmp_start_times = new ArrayList<Long>();
		List<Long> 	tmp_durations = new ArrayList<Long>();
		List<Boolean>	tmp_flags = new ArrayList<Boolean>();
		
		for ( int d=0; d<ap_durations.size(); d++){
			if ( tmp_ap_list.size() < MAX_RECORDS_FOR_ONE_SESSION ) {
				if (ap_durations.get(d) > SESSION_DURATION_WITHOUT_PPE ) {
					// Process the temperate AP list boundaries whose durations are
					// longer than SESSION_DURATION_WITHOUT_PPE;
					if (tmp_ap_list.size() == 0 || tmp_flags.get(tmp_flags.size()-1).booleanValue() == false){
						// Add this record to the final list
						final_records.add(new APRecord(ap_list.get(d), ap_start_times.get(d), ap_durations.get(d)));
						
						// clear the tmp data
						tmp_ap_list.clear();
						tmp_start_times.clear();
						tmp_durations.clear();
						tmp_flags.clear();
					} else {
						// copy the record
						tmp_ap_list.add(ap_list.get(d));
						tmp_start_times.add(ap_start_times.get(d));
						tmp_durations.add(ap_durations.get(d));
						tmp_flags.add(false);
						
						// Reduce PPE
						//final_records.addAll(PPDetector.RemovePP(tmp_ap_list, tmp_start_times, tmp_durations, tmp_flags));
						final_records.addAll(PPDetector2.removePingPong(tmp_ap_list, tmp_start_times, tmp_durations, tmp_flags));
						
						// clear the tmp data
						tmp_ap_list.clear();
						tmp_start_times.clear();
						tmp_durations.clear();
						tmp_flags.clear();
						// Add this record to the final list
						final_records.add(new APRecord(ap_list.get(d), ap_start_times.get(d), ap_durations.get(d)));
					}
				}
				// copy the record
				boolean flag = false;
				tmp_ap_list.add(ap_list.get(d));
				tmp_start_times.add(ap_start_times.get(d));
				tmp_durations.add(ap_durations.get(d));
				if (ap_durations.get(d) <= SESSION_DURATION_WITHOUT_PPE )
					flag = true;
				tmp_flags.add(flag);
			} else {
				// Reduce PPE
				//final_records.addAll(PPDetector.RemovePP(tmp_ap_list, tmp_start_times, tmp_durations, tmp_flags));
				final_records.addAll(PPDetector2.removePingPong(tmp_ap_list, tmp_start_times, tmp_durations, tmp_flags));
				
				// clear the tmp data
				tmp_ap_list.clear();
				tmp_start_times.clear();
				tmp_durations.clear();
				tmp_flags.clear();
			}
		}
		
		// Reduce PPE
		//final_records.addAll(PPDetector.RemovePP(tmp_ap_list, tmp_start_times, tmp_durations, tmp_flags));
		final_records.addAll(PPDetector2.removePingPong(tmp_ap_list, tmp_start_times, tmp_durations, tmp_flags));
		
		// clear the tmp data
		tmp_ap_list.clear();
		tmp_start_times.clear();
		tmp_durations.clear();
		tmp_flags.clear();
		// Process the final records
		return final_records;
	}
}

