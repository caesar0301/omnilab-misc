package sjtu.omnilab.bd.apps;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Arrays;

import org.apache.commons.io.FilenameUtils;
import sjtu.omnilab.bd.wifilogfilter.Utils;

/**
 * Separate the filtered logs (output of SyslogFilter.java) into individual users.
 * @author chenxm
 *
 */
public class SyslogSplitter {

	public static void main(String[] args) throws IOException {
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
        
        if(input_location.length() == 0 ) {
            System.out.println("Usage: sjtu.omnilab.bd.apps.SyslogSplitter -i <source> -o <destination>");
            System.exit(-1);
        }
        
        // for statistics
        long start  = System.currentTimeMillis();
        
        // split the raw data into individual users
        System.out.println("Split syslogs into users...");
        splitUsers(input_location, output_location);
        
        // print time
        System.out.println(String.format("Total time: %.3f sec", (System.currentTimeMillis() - start)/1000.0));
	}
	
	/**
     * Split the whole wifilogs into individual users.
     * @param input
     * @param output
     * @throws IOException
     */
    private static void splitUsers(String input, String output) throws IOException{
    	File[] files = Utils.getInputFiles(input);
        Utils.createFolder(output);
        Arrays.sort(files);
        for ( File file : files){
        	long start  = System.currentTimeMillis();
        	System.out.println(start/1000 + " " + file.getName());
        	String line = null;
        	BufferedReader iReader  = new BufferedReader(new FileReader(file));
        	while ((line = iReader.readLine()) != null) {
        		String[] parts = line.split("\t", 2);
        		if (parts.length == 2){
        			String mac = parts[0];
        			File outUserFile = Utils.createFile(FilenameUtils.concat(output, mac));
        			FileWriter oFileWriter = new FileWriter(outUserFile, true);
        			oFileWriter.write(line);
        			oFileWriter.close();
        		}
        	}
        	iReader.close();
        	System.out.println(String.format("Elapsed time: %.3f sec", (System.currentTimeMillis() - start)/1000.0));
        }
    }
}
