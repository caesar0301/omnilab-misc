package sjtu.omnilab.bd.apps;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.text.ParseException;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.zip.GZIPInputStream;

import org.apache.commons.io.FilenameUtils;
import sjtu.omnilab.bd.wifilogfilter.Utils;

/**   
 * Description: This class is used to filter the information which is related to 
 * location information and IP information in the ArubaSyslog. 
 * 
 * Output sample:
 * 6c71d96d8c4d	2013-10-11 23:50:53	AuthRequest	XXY-3F-09
 * 6c71d96d8c4d	2013-10-11 23:50:53	AssocRequest	XXY-3F-09
 * 6c71d96d8c4d	2013-10-11 23:50:53	AssocRequest	XXY-3F-09
 * b8782ec98a50	2013-10-11 23:59:52	IPRecycle	111.186.44.42
 * d4206d08b7b9	2013-10-11 23:50:28	AuthRequest	YXL-7-1F-03
 * d4206d08b7b9	2013-10-11 23:50:28	AssocRequest	YXL-7-1F-03
 * 
 * @author gwj, chenxm
 * Creation date: 2013.05.22
 */

public class SyslogFilter {
	
	private static BufferedWriter unmatchedBW = null; // for debugging
    
    public static void main(String[] args) throws FileNotFoundException, IOException, ParseException{
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
        
        if(input_location.length() == 0 || output_location.length() == 0) {
            System.out.println("Usage: sjtu.omnilab.bd.apps.SyslogFilter -i <source> -o <destination>");
            System.exit(-1);
        }
        
        // for statistics
        long start  = System.currentTimeMillis();
        
        // filter raw data first, and write to file with the same name of 
        // input file under folder "raw"
        System.out.println("Filter syslogs ...");
        filterData(input_location, output_location);
        
        // print time
        System.out.println(String.format("Total time: %.3f sec", (System.currentTimeMillis() - start)/1000.0));
        if ( unmatchedBW != null ) unmatchedBW.close();
    }
    
    /**
     * Filter the raw wifilogs with regex utilities.
     * @param input_file_location
     * @param output_file_location
     * @throws FileNotFoundException
     * @throws IOException
     */
    private static void filterData(String input_file_location, String output_file_location) throws FileNotFoundException, IOException{
        // Message CODE
        final int[] CODE_AUTHREQ = {501091,501092,501109};
        final int[] CODE_AUTHRES = {501093,501094,501110}; 		// not used
        final int[] CODE_DEAUTH = {501105,501080,501098,501099,501106,501107,501108,501111};    // from and to
        final int[] CODE_ASSOCREQ = {501095,501096,501097};
        final int[] CODE_ASSOCRES = {501100,501101,501112};  	// not used
        final int[] CODE_DISASSOCFROM = {501102,501104,501113};
        final int[] CODE_USERAUTH = {522008,522042,522038};     // Successful and failed
        final int[] CODE_USRSTATUS = {522005,522006,522026}; 	// User Entry added, deleted, and user miss
        final int[] CODE_USERROAM = {500010}; 					// not used
        final String regPrefix = "(?<time>\\w+\\s+\\d+\\s+(\\d{1,2}:){2}\\d{1,2}\\s+\\d{4})"; // date time and year
        final String regUserMac = "(?<usermac>([0-9a-f]{2}:){5}[0-9a-f]{2})";
        final String regApInfo = "(?<apip>(\\d{1,3}\\.){3}\\d{1,3})-(?<apmac>([0-9a-f]{2}:){5}[0-9a-f]{2})-(?<apname>[\\w-]+)";
        final Pattern REG_AUTHREQ = Pattern.compile(String.format("%s(.*)Auth\\s+request:\\s+%s:?\\s+(.*)AP\\s+%s", regPrefix, regUserMac, regApInfo), Pattern.CASE_INSENSITIVE);
        final Pattern REG_AUTHRES = Pattern.compile(String.format("%s(.*)Auth\\s+(success|failure):\\s+%s:?\\s+AP\\s+%s", regPrefix, regUserMac, regApInfo), Pattern.CASE_INSENSITIVE);
        final Pattern REG_DEAUTH = Pattern.compile(String.format("%s(.*)Deauth(.*):\\s+%s:?\\s+(.*)AP\\s+%s", regPrefix, regUserMac, regApInfo), Pattern.CASE_INSENSITIVE);
        final Pattern REG_ASSOCREQ = Pattern.compile(String.format("%s(.*)Assoc(.*):\\s+%s(.*):?\\s+(.*)AP %s", regPrefix, regUserMac, regApInfo), Pattern.CASE_INSENSITIVE);
        final Pattern REG_DISASSOCFROM = Pattern.compile(String.format("%s(.*)Disassoc(.*):\\s+%s:?\\s+AP\\s+%s", regPrefix, regUserMac, regApInfo), Pattern.CASE_INSENSITIVE);
        final Pattern REG_USERAUTH = Pattern.compile(String.format("%s(.*)\\s+username=(?<username>[^\\s]+)\\s+MAC=%s\\s+IP=(?<userip>(\\d{1,3}\\.){3}\\d{1,3})(.+)(AP=(?<apname>[^\\s]+))?", regPrefix, regUserMac), Pattern.CASE_INSENSITIVE);
        /**NOTE: before Oct. 14, 2013, WiFi networks in SJTU deploy the IP address of 111.186.0.0/18.
         * But after that (or confirmedly Oct. 17, 2013), local addresses are utlized to save the IP
         * resources. New IP addresses deployed in WiFi networks are:
         * Local1: 1001 111.186.16.1/20, New: 10.185.0.0/16
         * Local2: 1001 111.186.33.1/21, New: 10.186.0.0/16
         * Local3: 1001 111.186.40.1/21, New: 10.188.0.0/16
         * Local4: 1001 111.186.48.1/20, New: 10.187.0.0/16
         * Local5: 1001 111.186.0.1/20, New: 10.184.0.0/16
         */
        final Pattern REG_USRSTATUS = Pattern.compile(String.format("%s(.*)MAC=%s\\s+IP=(?<userip>(111\\.\\d+|10\\.18[4-8])(\\.\\d+){2})", regPrefix, regUserMac), Pattern.CASE_INSENSITIVE);
        
        //prepare for reading files one by one
        File[] files = Utils.getInputFiles(input_file_location);
        //read input_file one by one 
        for (File input_file : files) {
        	long start  = System.currentTimeMillis();
            System.out.println(start/1000 + " " + input_file.getName());
            
            // to read gziped file directly
            InputStream intputStream;
            String file_extention = FilenameUtils.getExtension(input_file.getName());
            if ( file_extention.equals("gz")) // if fille is compressed by gzip
                intputStream = new GZIPInputStream(new FileInputStream(input_file));
            else // otherwise
                intputStream = new FileInputStream(input_file);
            BufferedReader input_bufread = new BufferedReader(new InputStreamReader(intputStream));
            
            // filtered output file
            Utils.createFolder(output_file_location);
            File output_file = Utils.createFile(FilenameUtils.concat(output_file_location, FilenameUtils.getBaseName(input_file.getName())));
            FileWriter output_filewriter =new FileWriter(output_file, true);
            
            String line ="";
            while ((line = input_bufread.readLine()) != null) {      
                // filter out valid messages
            	String[] chops = new String[0];
            	try{
            		chops = line.split("<", 3);
            	} catch ( Exception e) {
            		System.err.println(e.toString());
            		System.out.println(line);
            		continue;
            	}
                if ( chops.length < 3 || chops[2].length() == 0 || chops[2].charAt(0) != '5')
                	continue;
                
                int messageCode = Integer.valueOf(chops[2].split(">", 2)[0]);
                boolean matched = false;
                if ( hasCodes(messageCode, CODE_AUTHREQ)){ // Auth request
                    Matcher matcher = REG_AUTHREQ.matcher(line);
                    if(matcher.find()){
                        matched = true;
                        String usermac = matcher.group("usermac").replaceAll(":", "");
                        String time = Utils.formattrans(matcher.group("time"));
                        output_filewriter.write(String.format("%s\t%s\t%s\t%s\n", usermac, time, "AuthRequest", matcher.group("apname")));
                    }
                } else if ( hasCodes(messageCode, CODE_DEAUTH) ){ // Deauth from and to
                    Matcher matcher = REG_DEAUTH.matcher(line);
                    if(matcher.find()){
                        matched = true;
                        String usermac = matcher.group("usermac").replaceAll(":", "");
                        String time = Utils.formattrans(matcher.group("time"));
                        output_filewriter.write( String.format("%s\t%s\t%s\t%s\n", usermac, time, "Deauth" ,matcher.group("apname")));
                    }
                } else if ( hasCodes(messageCode, CODE_ASSOCREQ) ){ // Association request
                    Matcher matcher = REG_ASSOCREQ.matcher(line);
                    if(matcher.find()){
                        matched = true;
                        String usermac = matcher.group("usermac").replaceAll(":", "");
                        String time = Utils.formattrans(matcher.group("time"));
                        output_filewriter.write( String.format("%s\t%s\t%s\t%s\n",usermac,time,"AssocRequest",matcher.group("apname")));
                    }
                } else if ( hasCodes(messageCode, CODE_DISASSOCFROM) ){ // Disassociation
                    Matcher matcher = REG_DISASSOCFROM.matcher(line);
                    if(matcher.find()){
                        matched = true;
                        String usermac = matcher.group("usermac").replaceAll(":", "");
                        String time = Utils.formattrans(matcher.group("time"));
                        output_filewriter.write( String.format("%s\t%s\t%s\t%s\n",usermac,time,"Disassoc", matcher.group("apname")));
                    }
                } else if ( hasCodes(messageCode, CODE_USERAUTH) ){  //username information, User authentication
                    Matcher matcher = REG_USERAUTH.matcher(line);
                    if(matcher.find()){
                        matched = true;
                        String usermac = matcher.group("usermac").replaceAll(":", "");
                        String time = Utils.formattrans(matcher.group("time"));
                        //System.out.println(record);
                        //apname is null if it is not there
                        output_filewriter.write( String.format("%s\t%s\t%s\t%s\t%s\t%s\n",usermac,time,"UserAuth", matcher.group("apname"),matcher.group("username"), matcher.group("userip")));
                    }
                } else if ( hasCodes(messageCode, CODE_USRSTATUS) ) { // User entry update status
                    Matcher matcher = REG_USRSTATUS.matcher(line);
                    if(matcher.find()){
                        matched = true;
                        String usermac = matcher.group("usermac").replaceAll(":", "");
                        String time = Utils.formattrans(matcher.group("time"));
                        String iPInfo = "IPAllocation";	// IP bond
                        if ( messageCode == 522005 ){ iPInfo = "IPRecycle"; }
                        /* From the output, we see multiple IPAllocation message between 
                         * the first allocation of specific IP and its recycling action.
                         */
                        output_filewriter.write(String.format("%s\t%s\t%s\t%s\n", usermac,time,iPInfo,matcher.group("userip")));
                    }
                }

                if( !matched && Utils.debug ){
//                	System.out.println(REG_AUTHREQ.pattern());
//                	System.out.println(REG_DEAUTH.pattern());
//                	System.out.println(REG_ASSOCREQ.pattern());
//                	System.out.println(REG_DISASSOCFROM.pattern());
//                	System.out.println(REG_USERAUTH.pattern());
//                	System.out.println(REG_USRSTATUS.pattern());
                	if ( unmatchedBW == null )
                		unmatchedBW = new BufferedWriter(new FileWriter("unmatched.txt"));
                	unmatchedBW.write(line+"\n");
                }
            }
            
            // close files
            output_filewriter.close();
            input_bufread.close();  
            System.out.println(String.format("Elapsed time: %.3f sec", (System.currentTimeMillis() - start)/1000.0));
        }
    }
    
    /**
     * Helper to check if specific message code is contained.
     * @param messageCode
     * @param codes
     * @return
     */
    private static boolean hasCodes(int messageCode, int[] codes){
        boolean flag = false;
        for ( int i : codes) {
            if (messageCode == i) {
                flag = true; 
                break;
            }
        }
        return flag;
    }
    
    /**
     * Put a user record into a map data structure.
     * @param userMac
     * @param record
     * @param map
     * @return
     */
    private static int putRecordMap(String userMac, String record, Map<String, List<String>> map){
        if ( !map.containsKey(userMac) ){
            map.put(userMac, new LinkedList<String>());
        }
        map.get(userMac).add(record);
        return 0;
    }
}
