package sjtu.omnilab.bd.apps;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.io.FilenameUtils;
import sjtu.omnilab.bd.wifilogfilter.SessionExtraction;
import sjtu.omnilab.bd.wifilogfilter.Utils;

/**
 * Extract wifi sessions from filtered logs (SyslogFilter.java).
 * Its a simple combination of SyslogSplitter.java and SyslogSessionExtractor.java.
 * @author chenxm
 *
 */
public class SyslogSplitterAndExtractor {

	public static void main(String[] args) throws IOException, ParseException {
		//Initial options
        String input_location = "";
        String output_location = "";
        
        // fetch command line options 
        int optSetting = 0;  
        for (; optSetting < args.length; optSetting++) {
            if ("-i".equals(args[optSetting])) {  
                input_location = args[++optSetting];  
            } else if ("-o".equals(args[optSetting])) {  
                output_location = args[++optSetting];
            }
        }
        
        if(input_location.length() == 0 ||  output_location.length() == 0 ) {
            System.out.println("Usage: sjtu.omnilab.bd.apps.SyslogSplitterAndExtractor -i <source> -o <destination>");
            System.exit(-1);
        }
        
        // for statistics
        long start  = System.currentTimeMillis();
        
        // split the raw data into individual users
        splitAndExtract(input_location, output_location);
        
        // print time
        System.out.println(String.format("Total time: %.3f sec", (System.currentTimeMillis() - start)/1000.0));
	}
	
	/**
     * Split the whole wifilogs into individual users.
     * @param input
     * @param output
     * @throws IOException
	 * @throws ParseException 
     */
    private static void splitAndExtract(String input, String output) throws IOException, ParseException{
    	File[] files = Utils.getInputFiles(input);
        Utils.createFolder(output);
        Arrays.sort(files);
        for ( File file : files){
        	Map<String, List<String>> macRecordMap = new HashMap<String, List<String>>();
        	long start  = System.currentTimeMillis();
        	System.out.println(start/1000 + " " + file.getName());
        	String line = null;
        	BufferedReader iReader  = new BufferedReader(new FileReader(file));
        	
        	System.out.println("Split syslogs into users...");
        	while ((line = iReader.readLine()) != null) {
        		String[] parts = line.split("\t", 2);
        		if (parts.length == 2){
        			String mac = parts[0];
        			if ( !macRecordMap.containsKey(mac) ){
        				macRecordMap.put(mac, new ArrayList<String>());
        			}
        			macRecordMap.get(mac).add(line);
        		}
        	}
        	iReader.close();
        	
        	System.out.println("Extract sessions...");
        	for ( String umac : macRecordMap.keySet()){
        		if ( Utils.debug )
        			System.out.println(umac);
        		
        		// extract session and save to file
                List<String> finalLines = SessionExtraction.extractSessions(macRecordMap.get(umac));
                
                // write into file
                BufferedWriter bw = new BufferedWriter(new FileWriter(FilenameUtils.concat(output, FilenameUtils.getName(file.getName())), true));
                for ( String l : finalLines )
                    bw.write(l + "\n");
                bw.close();
        	}
        	
        	macRecordMap.clear();
        	System.out.println(String.format("Elapsed time: %.3f sec", (System.currentTimeMillis() - start)/1000.0));
        }
    }
}
