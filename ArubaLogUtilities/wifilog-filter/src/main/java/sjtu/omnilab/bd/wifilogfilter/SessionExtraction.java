package sjtu.omnilab.bd.wifilogfilter;

import java.io.IOException;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.LinkedList;
import java.util.List;
import java.util.TreeMap;

/**
 * Main algorithm to extract user association session with AP.
 * @author Wenjuan Gong
 *
 */
public class SessionExtraction {
	private final static String ACTION_AUTH_REQUEST = "AuthRequest";
	private final static String ACTION_ASSOC_REQUEST =  "AssocRequest";
	private final static String ACTION_DEAUTH_REQUEST = "Deauth";
	private final static String ACTION_DEASSOS_REQUEST = "Disassoc";
	
	private final static String ACTION_IP_ALLOCATION = "IPAllocation";
	private final static String ACTION_IP_RECYCLE = "IPRecycle";
	private final static String ACTION_USER_AUTH = "UserAuth";
	
	private final static String ACTION_SESSION_START = "auth";
	private final static String ACTION_SESSION_END = "deauth";
	
	private final static String DATE_TIME_FORMAT = "yyyy-MM-dd HH:mm:ss";
	
	/**
	 * Main portal of user session extraction algorithm
	 * @param individualRawLines The filtered log messages for an individual user.
	 * @return The sessions extracted.
	 * @throws IOException
	 * @throws ParseException
	 */
    public static List<String> extractSessions(List<String> individualRawLines) throws IOException, ParseException{
        List<String> allLines = new LinkedList<String>();
        // sort lines
        // Note: we should order the logs with respect to timestamp only, not with the action (bug).
        Collections.sort(allLines, new Comparator<String>() {
			public int compare(String o1, String o2) {
				return compare(o1.split("\\t")[1], o2.split("\\t")[1]);
			}
		});
        // filter session info
        allLines = sessionInfoFilter(individualRawLines);
        // extract rough sessions
        allLines = extractRoughSessions(allLines);
        // adjust end times
        allLines = mergeSessions(adjustEndTime(allLines));
        
        return allLines;
    }
    
    /**
     * Filter out invalid and duplicate messages
     * @param allLines
     * @return
     */
    private static List<String> sessionInfoFilter(List<String> allLines){
    	List<String> filterLines = new LinkedList<String>();
        String auth_previous_time = "";
        String auth_previous_ap = "";
        String deauth_previous_time = "";
        String deauth_previous_ap = "";
        
        for ( String line : allLines ){
        	String[] parts = line.split("\\t");
        	if ( parts.length < 4 )
        		continue;
        	String mac = parts[0];
        	String time = parts[1];
        	String action = parts[2];
        	String ap = parts[3];

        	if(action.contains(ACTION_AUTH_REQUEST) || action.contains(ACTION_ASSOC_REQUEST)){
        		if(time.equals(auth_previous_time) && ap.equals(auth_previous_ap)){
        			// filter out duplicate messages
        			continue;
        		} else{
        			/*
        			 * line format:
        			 * usermac, timestamp, <Auth, Deauth>, apname
        			 */
        			filterLines.add(mac + "\t" + time + "\t" + ACTION_SESSION_START + "\t" + ap);
        			auth_previous_time = time;
        			auth_previous_ap = ap;
        		}
        	} else if (action.contains(ACTION_DEAUTH_REQUEST) || action.contains(ACTION_DEASSOS_REQUEST)) {
        		if(time.equals(deauth_previous_time) && ap.equals(deauth_previous_ap)){
        			continue;
        		} else{
        			/*
        			 * line format:
        			 * usermac, timestamp, <Auth, Deauth>, apname
        			 */
        			filterLines.add(mac + "\t" + time + "\t" + ACTION_SESSION_END + "\t" + ap);
        			deauth_previous_time = time;
        			deauth_previous_ap = ap;
        		}
        	} else{
        		/*
        		 * Remain the content of other lines
        		 */
        		filterLines.add(line);
        	} 
        }
        return filterLines;
    }
    
    
    private static List<String> extractRoughSessions(List<String> allLines) throws ParseException {
        List<String> roughSessions = new LinkedList<String>();
        //prepare to store the "Auth" log, K: ap name , V: date_string
        TreeMap<String, String> ap_auth_tmap = new TreeMap<String, String>();                   
        //start exacting the movement session
        String previous_ap = "";
        String previous_action = "";
        for ( String line : allLines ){
        	String[] parts = line.split("\\t");
        	if ( parts.length < 4 )
        		continue;
        	String mac = parts[0];
        	String date_string = parts[1];
        	String action = parts[2];
        	String ap = parts[3];
        	
            if(action.equals(ACTION_SESSION_START)){    //auth request log
                if(ap_auth_tmap.containsKey(ap)){
                    //the treemap already has the ap name
                    if(ap.equals(previous_ap) && action.equals(previous_action)){
                        //discard
                        if (Utils.debug){
                        	System.out.println("repeating auth log!");
                        }
                        continue;
                    } else{
                        // replace the previous one
                    	// currently, we do not end an auth (without deauth) with another auth.
                        ap_auth_tmap.put(ap, date_string);
                    }
                }
                else{
                    //a new ap name
                    ap_auth_tmap.put(ap, date_string);
                }
            } else if (action.equals(ACTION_SESSION_END)){    //"Deauth log"
                if(ap_auth_tmap.containsKey(ap)){
                    //movement exact
                    String start_time_string = ap_auth_tmap.get(ap);
                    String end_time_string = date_string;
                    DateFormat df = new SimpleDateFormat(DATE_TIME_FORMAT);
                    Date start_time = df.parse(start_time_string);
                    Date end_time = df.parse(end_time_string);
                    long duration = (end_time.getTime() - start_time.getTime())/1000;
                    /*
                     * Write into the output file in the format of
                     * USER_MAC, START_TIME, END_TIME, DURATION, AP_NAME
                     */
                    roughSessions.add(mac + "\t" + start_time_string + "\t" + end_time_string + "\t" + duration + "\t" + ap);
                    //remove the auth time with this ap in the ap_auth_tmap
                    ap_auth_tmap.remove(ap);
                } else{    
                    //discard
                    if (Utils.debug) {
                    	System.out.println("Can not find the ap! discard!!!");
                    }
                    continue;
                }
            } else {
            	/*
            	 * Add other lines as what they are for future usage. 
            	 */
            	roughSessions.add(line);
            }
            previous_ap = ap;
            previous_action = action;
        }

        return roughSessions;
    }
    
    
    private static List<String> adjustEndTime(List<String> allLines) throws ParseException {
        List<String> finalLines = new LinkedList<String>();
        if( allLines.size() == 0 ){
        	//an empty file
        	return finalLines;
        }
        
        DateFormat df = new SimpleDateFormat(DATE_TIME_FORMAT);
        String previous_line = "";
        String previous_enddate_string = "";
        int last_read = 0;
        for ( last_read = 0; last_read < allLines.size(); last_read++){
        	previous_line = allLines.get(last_read);
        	if(previous_line.contains(ACTION_IP_ALLOCATION)||previous_line.contains(ACTION_IP_RECYCLE)||previous_line.contains(ACTION_USER_AUTH)){
                finalLines.add(previous_line);
                continue;
            } else {
            	previous_enddate_string = previous_line.split("\\t")[2];
                break;
            }
        }
        
        for ( int i = last_read+1; i < allLines.size(); i++ ) {
            String line = allLines.get(i);
            if(line.contains(ACTION_IP_ALLOCATION)||line.contains(ACTION_IP_RECYCLE)||line.contains(ACTION_USER_AUTH)){
                finalLines.add(line);
                continue;
            }
            
            String startdate_string = line.split("\\t")[1];
            String enddate_string = line.split("\\t")[2];
            Date startdate = df.parse(startdate_string);
            Date previous_enddate = df.parse(previous_enddate_string);
            
            long diff = previous_enddate.getTime() - startdate.getTime();
            
            if(diff <= 0){
                //write the previous line into the output_file
                finalLines.add(previous_line);
            }
            else{
                //change the end time of the previous line to the start time of the following line , and write into output file
                String write_line = previous_line.replace(previous_enddate_string, startdate_string);
                finalLines.add(write_line);
            }
            
            previous_line = line;
            previous_enddate_string = enddate_string;
        }
        
        //write the last line into the output file
        if(previous_line != null)
            finalLines.add(previous_line);
        return finalLines;
    }
    
    
    private static List<String> mergeSessions(List<String> allLines) throws ParseException {
        List<String> finalLines = new LinkedList<String>();
        
        DateFormat df = new SimpleDateFormat(DATE_TIME_FORMAT);
        
        String previous_line = "";
        String previous_mac = "";
        String previous_startdate_string = "";
        String previous_enddate_string = "";
        String previous_duration_string = "";
        String previous_ap = "";
        long duration = 0;
        int last_read = 0;
        if( allLines.size() != 0 ){
            previous_line = allLines.get(0);
            if(previous_line.contains(ACTION_IP_ALLOCATION)||previous_line.contains(ACTION_IP_RECYCLE)||previous_line.contains(ACTION_USER_AUTH)){
                finalLines.add(previous_line);
                for ( int i = 1; i<allLines.size(); i++){
                    previous_line = allLines.get(i);
                    last_read = i;
                    if(previous_line.contains(ACTION_IP_ALLOCATION)||previous_line.contains(ACTION_IP_RECYCLE)||previous_line.contains(ACTION_USER_AUTH)){
                        finalLines.add(previous_line);
                        continue;
                    } else {
                    	String[] parts = previous_line.split("\\t");
                    	if ( parts.length < 5 )
                    		continue;
                    	previous_mac = parts[0];
                    	previous_startdate_string = parts[1];
                    	previous_enddate_string= parts[2];
                    	previous_duration_string = parts[3];
                    	previous_ap = parts[4];
                        duration = Long.parseLong(previous_duration_string);
                        break;
                    }
                }
            }
            else{ 
                String[] parts = previous_line.split("\\t");
            	if ( parts.length == 5 ){
            		previous_mac = parts[0];
                	previous_startdate_string = parts[1];
                	previous_enddate_string= parts[2];
                	previous_duration_string = parts[3];
                	previous_ap = parts[4];
                    duration = Long.parseLong(previous_duration_string);
            	}
            }
        }
        else    //an empty file
            return finalLines;

        String line ="";
        for ( int i=last_read+1; i<allLines.size(); i++ ) {
            line = allLines.get(i);
            if(line.contains(ACTION_IP_ALLOCATION)||line.contains(ACTION_IP_RECYCLE)||line.contains(ACTION_USER_AUTH)){
                finalLines.add(line);
                continue;
            }
            String[] parts = line.split("\\t");
        	if ( parts.length < 5 )
        		continue;
            String startdate_string = parts[1];
            String enddate_string = parts[2];
            String duration_string = parts[3];
            String ap = parts[4];
            
            Date previous_enddate = df.parse(previous_enddate_string);
            Date startdate = df.parse(startdate_string);
            long diff = (startdate.getTime() - previous_enddate.getTime())/1000;
            
            long current_duration = Long.parseLong(duration_string);
            
            if(ap.equals(previous_ap) && diff <= 10){
                //merge
                previous_enddate_string = enddate_string;
                duration += (current_duration + diff);
            }
            else{
                //write the session into the output file
                finalLines.add(previous_mac + "\t" + previous_startdate_string + "\t" + previous_enddate_string + "\t" + duration + "\t" + previous_ap);
                
                //update
                previous_ap = ap;
                previous_startdate_string = startdate_string;
                previous_enddate_string = enddate_string;
                duration = current_duration;
            }
        }
        
        if(!previous_startdate_string.equals(""))
            finalLines.add(previous_mac + "\t" + previous_startdate_string + "\t" + previous_enddate_string + "\t" + duration + "\t" + previous_ap);
        return finalLines;
    }
}
