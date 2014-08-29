package sjtu.omnilab.bd.wifilogfilter;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Utils {
	
	/** public constants */
	public static boolean debug = false;
	
    //This function is used to change the date format from "May 4" to "2013-05-04"
    public static String formattrans(String date_string){
        //Prepare for the month name for date changing
        TreeMap<String, String> month_tmap = new TreeMap<String, String>();
        month_tmap.put("Jan", "01");
        month_tmap.put("Feb", "02");
        month_tmap.put("Mar", "03");
        month_tmap.put("Apr", "04");
        month_tmap.put("May", "05");
        month_tmap.put("Jun", "06");
        month_tmap.put("Jul", "07");
        month_tmap.put("Aug", "08");
        month_tmap.put("Sep", "09");
        month_tmap.put("Oct", "10");
        month_tmap.put("Nov", "11");
        month_tmap.put("Dec", "12");
        //change the date from "May 4" to "2013-05-04"
        String date_reg = "(?<month>\\w+)\\s+(?<day>\\d+)\\s+(?<time>(\\d{1,2}:){2}\\d{1,2})\\s+(?<year>\\d{4})";
        Pattern date_pattern = Pattern.compile(date_reg);
        Matcher date_matcher = date_pattern.matcher(date_string);
        if(! date_matcher.find()) return null;
        
        String year_string=date_matcher.group("year");
        //change the month format
        String month_string = date_matcher.group("month");
        if(month_tmap.containsKey(month_string)){
        	month_string = month_tmap.get(month_string);
        }else{
            System.out.println("Can not find the month!!!");
        }
        //change the day format
        String day_string = date_matcher.group("day");
        int day_int = Integer.parseInt(day_string);
        if(day_int < 10){
        	day_string = "0" + Integer.toString(day_int);
        }else{
        	day_string = Integer.toString(day_int);
        }
        String time_string = date_matcher.group("time");
        return String.format("%s-%s-%s %s", year_string, month_string, day_string, time_string);
    }
    
    /**
     * Get the input file list of specific input file/folder.
     * @param input File or folder path.
     * @return
     */
    public static File[] getInputFiles(String input){
        File inputFile = new File(input);
        File[] files = new File[1];
        if ( inputFile.isFile() ){
            files[0] = inputFile;
        } else {
            files = inputFile.listFiles(); 
        }
        // sort files
        Arrays.sort(files);
        return files;
    }
    
    /**
     * Create a new folder
     * @param path
     * @return
     */
    public static File createFolder(String path){
    	File folder = new File(path);
        if ( ! folder.exists() ){
        	folder.mkdirs();
        }
        return folder;
    }
    
    /**
     * Create a new file.
     * @param file
     * @return
     * @throws IOException
     */
    public static File createFile(String file) throws IOException{
    	File newFile = new File(file);
        if(!newFile.exists()){  
        	newFile.createNewFile();  
        }
        return newFile;
    }
}
