package cn.edu.sjtu.omnilab.livewee.kapro;

import java.io.*;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Cleanse and format Aruba Wifi logs by filtering out unwanted log numbers.
 *
 * Input:
 * Raw or original Aruba syslog files.
 *
 * Output:
 * 6c71d96d8c4d,2013-10-11 23:50:53,0,XXY-3F-09
 * 6c71d96d8c4d,2013-10-11 23:50:53,1,XXY-3F-09
 *
 * Update:
 * Before Oct. 14, 2013, WiFi networks in SJTU deploy the IP address of 111.186.0.0/18.
 * After that (or confirmedly Oct. 17, 2013), local addresses are utlized to save the IP
 * resources. New IP addresses deployed in WiFi networks are:
 * Local1: 1001 111.186.16.1/20, New: 10.185.0.0/16
 * Local2: 1001 111.186.33.1/21, New: 10.186.0.0/16
 * Local3: 1001 111.186.40.1/21, New: 10.188.0.0/16
 * Local4: 1001 111.186.48.1/20, New: 10.187.0.0/16
 * Local5: 1001 111.186.0.1/20, New: 10.184.0.0/16
 *
 * @Author chenxm
 * @Version 2.1
 */

/**
 * Message encoding
 */
class WIFICode {
    public static final int Invalid = -1024;
    public static final int AuthRequest = 0;
    public static final int Deauth = 1;
    public static final int AssocRequest = 2;
    public static final int Disassoc = 3;
    public static final int UserAuth = 4;
    public static final int IPAllocation = 5;
    public static final int IPRecycle = 6;
    public static final int UserRoaming = 7;
    public static final int UnencDataFrame = 8;
    public static final int RogueAPDetected = 9;
    public static final int StationNewUp = 10;
    public static final int StationDepart = 11;
}

interface PatternExt {
    public String parse(String message);
}

public class WifilogFilter {

    /**
     * Message decodes we depend on
     */
    final static int[] CODE_AUTHREQ = {501091, 501092, 501109};
    final static int[] CODE_AUTHRES = {501093, 501094, 501110};
    final static int[] CODE_DEAUTH = {501105, 501080, 501098, 501099, 501106, 501107, 501108, 501111};
    final static int[] CODE_ASSOCREQ = {501095, 501096, 501097};
    final static int[] CODE_ASSOCRES = {501100, 501101, 501112};
    final static int[] CODE_DISASSOC = {501102, 501104, 501113};
    final static int[] CODE_USERAUTH = {522008, 522042, 522038};
    final static int[] CODE_IPSTATUS = {522005, 522006, 522026};
    final static int[] CODE_USERROAM = {500010};
    final static int[] CODE_UNENCDF = {127065};
    final static int[] CODE_ROGUEAP = {127037};
    final static int[] CODE_STAUPDN = {522035, 522036};

    /**
     * Generic patterns to extract message fields:
     */
    final static String TIMPRE = "\\w+\\s+\\d+\\s+(?:\\d{1,2}:){2}\\d{1,2}\\s+\\d{4}";
    final static String USRMAC = "(?:[0-9a-f]{2}:){5}[0-9a-f]{2}";
    final static String IPADDR = "(?:\\d{1,3}\\.){3}\\d{1,3}";
    final static String APNAME = "[\\w-]+";
    final static String APINFO = "((?:\\d{1,3}\\.){3}\\d{1,3})-((?:[0-9a-f]{2}:){5}[0-9a-f]{2})-([\\w-]+)";

    /**
     * Authentication requests
     * groups (starting with 1): time, usename, apip, apmac, apname
     */
    final static Pattern AUTHREQ = Pattern.compile(String.format(
            "(%s)(?:.*)auth\\s+request:\\s+(%s):?\\s+(?:.*)AP\\s+%s",
            TIMPRE, USRMAC, APINFO), Pattern.CASE_INSENSITIVE);
    final static PatternExt PE_AUTHREQ = new PatternExt() {
        @Override
        public String parse(String message) {
            String formatted = null;
            Matcher matcher = AUTHREQ.matcher(message);
            if (matcher.find()) {
                String time = formatTrans(matcher.group(1));
                String usermac = matcher.group(2).replaceAll(":", "");
                String apname = matcher.group(5);
                formatted = String.format("%s,%s,%s,%s", usermac, time, WIFICode.AuthRequest, apname);
            }
            return formatted;
        }
    };

    /**
     * Authentication responses
     */
    final static Pattern AUTHRES = Pattern.compile(String.format(
            "(%s)(?:.*)auth\\s+(success|failure):\\s+(%s):?\\s+AP\\s+%s",
            TIMPRE, USRMAC, APINFO), Pattern.CASE_INSENSITIVE);

    /**
     * Deauthentication
     */
    final static Pattern DEAUTH = Pattern.compile(String.format(
            "(%s)(?:.*)deauth(?:.*):\\s+(%s):?\\s+(?:.*)AP\\s+%s",
            TIMPRE, USRMAC, APINFO), Pattern.CASE_INSENSITIVE);
    final static PatternExt PE_DEAUTH = new PatternExt() {
        @Override
        public String parse(String message) {
            String formatted = null;
            Matcher matcher = DEAUTH.matcher(message);
            if (matcher.find()) {
                String time = formatTrans(matcher.group(1));
                String usermac = matcher.group(2).replaceAll(":", "");
                String apname = matcher.group(5);
                formatted = String.format("%s,%s,%s,%s", usermac, time, WIFICode.Deauth, apname);
            }
            return formatted;
        }
    };

    /**
     * Association requests
     */
    final static Pattern ASSOCREQ = Pattern.compile(String.format(
            "(%s)(?:.*)assoc(?:.*):\\s+(%s)(?:.*):?\\s+(?:.*)AP\\s+%s",
            TIMPRE, USRMAC, APINFO), Pattern.CASE_INSENSITIVE);
    final static PatternExt PE_ASSOCREQ = new PatternExt() {
        @Override
        public String parse(String message) {
            String formatted = null;
            Matcher matcher = ASSOCREQ.matcher(message);
            if (matcher.find()) {
                String time = formatTrans(matcher.group(1));
                String usermac = matcher.group(2).replaceAll(":", "");
                String apname = matcher.group(5);
                formatted = String.format("%s,%s,%s,%s", usermac, time, WIFICode.AssocRequest, apname);
            }
            return formatted;
        }
    };

    /**
     * Disassociation
     */
    final static Pattern DISASSOC = Pattern.compile(String.format(
            "(%s)(?:.*)disassoc(?:.*):\\s+(%s):?\\s+AP\\s+%s",
            TIMPRE, USRMAC, APINFO), Pattern.CASE_INSENSITIVE);
    final static PatternExt PE_DISASSOC = new PatternExt() {
        @Override
        public String parse(String message) {
            String formatted = null;
            Matcher matcher = DISASSOC.matcher(message);
            if (matcher.find()) {
                String time = formatTrans(matcher.group(1));
                String usermac = matcher.group(2).replaceAll(":", "");
                String apname = matcher.group(5);
                formatted = String.format("%s,%s,%s,%s", usermac, time, WIFICode.Disassoc, apname);
            }
            return formatted;
        }
    };

    /**
     * User Authentication
     * groups (starting with 1): time, usename, usermac, userip, apname
     */
    final static Pattern USERAUTH = Pattern.compile(String.format(
            "(%s)(?:.*)\\s+username=([^\\s]+)\\s+MAC=(%s)\\s+IP=(%s)(?:.+)(?:AP=(%s))?",
            TIMPRE, USRMAC, IPADDR, APNAME), Pattern.CASE_INSENSITIVE);
    final static PatternExt PE_USERAUTH = new PatternExt() {
        @Override
        public String parse(String message) {
            String formatted = null;
            Matcher matcher = USERAUTH.matcher(message);
            if (matcher.find()) {
                String time = formatTrans(matcher.group(1));
                String username = matcher.group(2);
                String usermac = matcher.group(3).replaceAll(":", "");
                String userip = matcher.group(4);
                String apname = null;
                try {
                    apname = matcher.group(5);
                } catch (Exception e) {
                    //apname is null if it is not there
                }
                formatted = String.format("%s,%s,%s,%s,%s,%s", usermac, time, WIFICode.UserAuth, username, userip, apname);
            }
            return formatted;
        }
    };

    /**
     * L3 layer status
     * groups (starting with 1): time, usermac, userip
     */
    final static Pattern IPSTATUS = Pattern.compile(String.format(
            "(%s)(?:.*)MAC=(%s)\\s+IP=((?:111\\.\\d+|10\\.18[4-8])(?:\\.\\d+){2})",
            TIMPRE, USRMAC), Pattern.CASE_INSENSITIVE);
    final static PatternExt PE_IPSTATUS = new PatternExt() {
        @Override
        public String parse(String message) {
            String formatted = null;
            Matcher matcher = IPSTATUS.matcher(message);
            if (matcher.find()) {
                String time = formatTrans(matcher.group(1));
                String usermac = matcher.group(2).replaceAll(":", "");
                String userip = matcher.group(3);

                int action = WIFICode.IPAllocation;    // IP bond
                if (extractMsgCode(message) == 522005) {
                    action = WIFICode.IPRecycle;
                }
                /* From the output, we see multiple IPAllocation message between
                 * the first allocation of specific IP and its recycling action.
                 */
                formatted = String.format("%s,%s,%s,%s", usermac, time, action, userip);
            }
            return formatted;
        }
    };

    /**
     * Roaming actions
     */
    final static Pattern USRROAM = Pattern.compile(String.format(
            "(%s)(?:.*)station\\s+(%s),(?:.*)AP\\s+(%s)",
            TIMPRE, USRMAC, APNAME), Pattern.CASE_INSENSITIVE);
    final static PatternExt PE_USRROAM = new PatternExt() {
        @Override
        public String parse(String message) {
            String formatted = null;
            Matcher matcher = USRROAM.matcher(message);
            if (matcher.find()) {
                String time = formatTrans(matcher.group(1));
                String usermac = matcher.group(2).replaceAll(":", "");
                String apname = matcher.group(3);
                formatted = String.format("%s,%s,%s,%s", usermac, time, WIFICode.UserRoaming, apname);
            }
            return formatted;
        }
    };

    /**
     * Unencrypted data frame alert
     */
    final static Pattern UNENCDF = Pattern.compile(String.format(
            "(%s)(?:.*)\\|AP\\s+(%s)(?:[^\\|]*\\|)(?:.*)a valid client \\((%s)\\)",
            TIMPRE, APNAME, USRMAC), Pattern.CASE_INSENSITIVE);
    final static PatternExt PE_UNENCDF = new PatternExt() {
        @Override
        public String parse(String message) {
            String formatted = null;
            Matcher matcher = UNENCDF.matcher(message);
            if (matcher.find()) {
                String time = formatTrans(matcher.group(1));
                String apname = matcher.group(2);
                String usermac = matcher.group(3).replaceAll(":", "");
                formatted = String.format("%s,%s,%s,%s", usermac, time, WIFICode.UnencDataFrame, apname);
            }
            return formatted;
        }
    };

    /**
     * Detected a client associated with a Rogue access point.
     */
    final static Pattern ROGUEAP = Pattern.compile(String.format(
            "(%s)(?:.*)\\|AP\\s+(%s)(?:[^\\|]*\\|)(?:.*)detected a client (%s)",
            TIMPRE, APNAME, USRMAC), Pattern.CASE_INSENSITIVE);
    final static PatternExt PE_ROGUEAP = new PatternExt() {
        @Override
        public String parse(String message) {
            String formatted = null;
            Matcher matcher = ROGUEAP.matcher(message);
            if (matcher.find()) {
                String time = formatTrans(matcher.group(1));
                String apname = matcher.group(2);
                String usermac = matcher.group(3).replaceAll(":", "");
                formatted = String.format("%s,%s,%s,%s", usermac, time, WIFICode.RogueAPDetected, apname);
            }
            return formatted;
        }
    };

    /**
     * System detected a new wireless station or departure of a wireless station.
     */
    final static Pattern STAUPDN = Pattern.compile(String.format(
            "(%s)(?:.*)MAC=(%s) station (up|dn)(?:.*)AP-name=(%s)",
            TIMPRE, USRMAC, APNAME), Pattern.CASE_INSENSITIVE);
    final static PatternExt PE_STAUPDN = new PatternExt() {
        @Override
        public String parse(String message) {
            String formatted = null;
            Matcher matcher = STAUPDN.matcher(message);
            if (matcher.find()) {
                String time = formatTrans(matcher.group(1));
                String usermac = matcher.group(2).replaceAll(":", "");
                String status = matcher.group(3);
                String apname = matcher.group(4);
                int code = WIFICode.StationNewUp;
                if ( status == "dn" )
                    code = WIFICode.StationDepart;
                formatted = String.format("%s,%s,%s,%s", usermac, time, code, apname);
            }
            return formatted;
        }
    };

    /**
     * Extract message code from raw logs.
     * @param message
     * @return
     */
    private static int extractMsgCode(String message) {
        String[] chops = new String[0];
        try {
            chops = message.split("<", 3);
            return Integer.valueOf(chops[2].split(">", 2)[0]);
        } catch (Exception e) {
            return WIFICode.Invalid;
        }
    }

    /**
     * Helper to check if specific message code is contained.
     */
    private static boolean hasCodes(int messageCode, int[] codes) {
        boolean flag = false;
        for (int i : codes) {
            if (messageCode == i) {
                flag = true;
                break;
            }
        }
        return flag;
    }

    /**
     * This function is used to change the date format
     * from "May 4 2013" to "2013-05-04".
     */
    private static String formatTrans(String date_string){
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
        // month: group(1), day: group(2), time: group(3), year: group(4)
        String date_reg = "(\\w+)\\s+(\\d+)\\s+((?:\\d{1,2}:){2}\\d{1,2})\\s+(\\d{4})";
        Pattern date_pattern = Pattern.compile(date_reg);
        Matcher date_matcher = date_pattern.matcher(date_string);
        if(! date_matcher.find())
            return null;

        String year_string=date_matcher.group(4);
        //change the month format
        String month_string = date_matcher.group(1);
        if(month_tmap.containsKey(month_string)){
            month_string = month_tmap.get(month_string);
        }else{
            System.out.println("Can not find the month!!!");
        }
        //change the day format
        String day_string = date_matcher.group(2);
        int day_int = Integer.parseInt(day_string);
        if(day_int < 10){
            day_string = "0" + Integer.toString(day_int);
        }else{
            day_string = Integer.toString(day_int);
        }

        String time_string = date_matcher.group(3);
        return String.format("%s-%s-%s %s", year_string, month_string, day_string, time_string);
    }

    /**
     * Cleanse and reformat raw Wifi logs.
     * @param message
     * @return
     * @throws IOException
     */
    public static String cleanse(String message) throws IOException {
        String cleanLog = null;

        int code = extractMsgCode(message);
        if (code == WIFICode.Invalid || (code/100000 != 1 && code/100000 != 5))
            return cleanLog;

        if (hasCodes(code, CODE_AUTHREQ)) {
            cleanLog = PE_AUTHREQ.parse(message);
        } else if (hasCodes(code, CODE_DEAUTH)) {
            cleanLog = PE_DEAUTH.parse(message);
        } else if (hasCodes(code, CODE_ASSOCREQ)) {
            cleanLog = PE_ASSOCREQ.parse(message);
        } else if (hasCodes(code, CODE_DISASSOC)) {
            cleanLog = PE_DISASSOC.parse(message);
        } else if (hasCodes(code, CODE_USERAUTH)) {
            cleanLog = PE_USERAUTH.parse(message);
        } else if (hasCodes(code, CODE_IPSTATUS)) {
            cleanLog = PE_IPSTATUS.parse(message);
        } else if (hasCodes(code, CODE_USERROAM)) {
            cleanLog = PE_USRROAM.parse(message);
        } else if (hasCodes(code, CODE_UNENCDF)) {
            cleanLog = PE_UNENCDF.parse(message);
        } else if (hasCodes(code, CODE_ROGUEAP)) {
            cleanLog = PE_ROGUEAP.parse(message);
        } else if (hasCodes(code, CODE_STAUPDN)) {
            cleanLog = PE_STAUPDN.parse(message);
        }

        return cleanLog;
    }
}