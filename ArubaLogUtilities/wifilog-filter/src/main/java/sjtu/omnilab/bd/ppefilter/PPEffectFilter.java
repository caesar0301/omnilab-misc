package sjtu.omnilab.bd.ppefilter;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.TimeZone;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

class DebugFlag {
	static boolean debug = true;
}

public class PPEffectFilter {
	public static void main(String[] args) throws IOException{
		
		/**
	     *Parse the command line options (input_file_location, output_file_location)
	     *usage: java cn.edu.sjtu.omnilab.arubasyslogparser.SyslogFilter [options]
	     *Options:
	     *-i  --input_file_location
	     *-o  --output_file_location
	     */
	
    	//Initial options
        String input_file_location = "";
        String output_file_location = "";
        
        // fetch command line options 
        int optSetting = 0;  
        for (; optSetting < args.length; optSetting++) {  
            if ("-i".equals(args[optSetting])) {  
                input_file_location = args[++optSetting];  
            } else if ("-o".equals(args[optSetting])) {  
                output_file_location = args[++optSetting];  
            }
        }
        
        //prepare for reading files one by one
  		File input_folder = null;  
  		input_folder = new File(input_file_location);  
  		File[] files = input_folder.listFiles(); 
  		
  		//String input_file_path = "";
  		String uid = "";
  		String input_file_name = "";
  		String output_file = "";
  		
  		// Skip invalid files without name format \d+.mv
  		String filename_regex = "[\\d\\w.]+.mv$";
  		Pattern p = Pattern.compile(filename_regex);
  		Matcher m = null;
		
  		for (File input_file : files) {
  			
  			//extract input_file_name as output_file_name
  			//input_file_path = input_file.getAbsolutePath();
  		    input_file_name = input_file.getName();
  		    
  		    // Skip invalid files without name format \d+.mv
  		    m = p.matcher(input_file_name);
  		    if ( m.find() == false)
  		    	continue;	// to skip
  		    
  		    uid = input_file_name.split("\\.")[0];
  		    //System.out.println(output_file_name);
  		    output_file = output_file_location + uid;
  		    
  		    // Input stream
  			FileReader ifr = new FileReader(input_file);
  			BufferedReader ibr = new BufferedReader(ifr);
  			
  			// Create parent directories if they are not available.
  			File output_folder = new File(output_file_location);
  			if ( !output_folder.exists() )
  				output_folder.mkdirs();
  			
  			// Output stream
  			File file = new File(output_file);	
            if(!file.exists()) {
                if(!file.createNewFile()) {
                	System.out.println("Can't create file.");
                }
            }
            
  			FileWriter ofr = new FileWriter(file);
  			BufferedWriter obr = new BufferedWriter(ofr);
  			
  			// Processing one file for a user
  			String line ="";
  			String [] ap_info;
  			ConvSession cs = null;
  			
  			while ((line = ibr.readLine()) != null) {
  				line = line.replaceAll("[\\n\\r]*","");
  				
  				// Read the conversation sessions
  				// Each session ends with "OFF" flag.
  				// Each file will be split into sessions as 
  				// count of "OFF"'s
  				if ( cs == null )
  					cs = new ConvSession(uid);
				ap_info = line.split("\\t");
				
				if ( ap_info[1].equals("OFF") == false && ibr.ready() == true) {
					// If the last line is without OFF
					// Add a fake OFF signs to the session records
					cs.addRecord(Long.parseLong(ap_info[0]), ap_info[1]);
					continue;
				}
				cs.addRecord(Long.parseLong(ap_info[0]), "OFF");
				
				// Filter the Ping-Pong Effect on the basis of each session,
				// and write the new session into an output file.
				List<ApRecord> final_records = cs.removePingPongEffect();
				SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
				TimeZone tz = TimeZone.getTimeZone("GMT-04:00");	//New York timezone
				df.setTimeZone(tz);
				for ( ApRecord r : final_records) {
					Date start = new Date(r.start_time*1000);
					Date end = new Date((r.start_time+r.duration)*1000);
					obr.write(r.name+"\t"+df.format(start)+"\t"+r.duration+"\t"+df.format(end)+"\n");
					//System.out.println(r.name+"\t"+r.start_time+"\t"+r.duration);
				}
				//obr.write("OFF\n");
				
				// Reset to start a new session
				cs = null;
  			}
  			ibr.close();
  			ifr.close();
			obr.close();
			ofr.close();
  		}
	}
}
