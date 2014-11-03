package sjtu.omnilab.bd.apps;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.text.ParseException;
import java.util.LinkedList;
import java.util.List;

import org.apache.commons.io.FilenameUtils;
import sjtu.omnilab.bd.wifilogfilter.SessionExtraction;
import sjtu.omnilab.bd.wifilogfilter.Utils;

/**
 * This class extract the wifi sessions from filtered wifi logs, which is output by SyslogFilter.java.
 * Output format: (usermac, STime, ETime, Dur, AP)
 * ec55f9c3c9f9    2013-09-29 00:37:40 2013-09-29 00:37:40 0   MLXY-3F-08
 * 50ead62002f7    2013-09-29 06:16:12 2013-09-29 06:16:31 19  LXZL-4F-03
 * 40f3088b77ff    2013-09-29 00:43:32 2013-09-29 00:43:48 23  MH-LXZL-2
 * 40f3088b77ff    2013-09-29 00:43:38 IPAllocation    111.186.40.54
 * 
 * @author chenxm
 *
 */
public class SyslogSessionExtractor {

	public static void main(String[] args) throws IOException, ParseException {
		// Initial options
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
        
        if(input_location.length() == 0 ) {
            System.out.println("Usage: sjtu.omnilab.bd.apps.SyslogSessionExtractor -i <source> -o <destination>>");
            System.exit(-1);
        }
        
        // for statistics
        long start  = System.currentTimeMillis();
        
        // reading filtered files one by one to extract user sessions
        System.out.println("Extracting user trace sessions from raw logs ...");
        Utils.createFolder(output_location);
        File[] user_files = Utils.getInputFiles(input_location);
        for (File file : user_files) {
        	String umac = file.getName();
        	System.out.println(System.currentTimeMillis() + " " + umac);
        	// read the file
            BufferedReader reader = new BufferedReader(new FileReader(file));
            String thisLine = "";
            List<String> allLines = new LinkedList<String>();
            // read each line
            while ((thisLine = reader.readLine()) != null) {
                thisLine = thisLine.replaceAll("[\\r\\n]", "");
                if ( thisLine.length() == 0 ) { continue; }
                allLines.add(thisLine);
            }
        	// extract session and save to file
            allLines = SessionExtraction.extractSessions(allLines);
            // write into file
            BufferedWriter bw = new BufferedWriter(new FileWriter(FilenameUtils.concat(output_location, umac)));
            for ( String l : allLines )
                bw.write(l + "\n");
            bw.close();
            reader.close();
        }
        
        // print time
        System.out.println(String.format("Total time: %.3f sec", (System.currentTimeMillis() - start)/1000.0));
	}
}
