package cn.edu.sjtu.omnilab.livewee.kc;

import org.yaml.snakeyaml.Yaml;
import org.yaml.snakeyaml.constructor.SafeConstructor;

import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

/**
 * Given a AP name string, this function return the description of the building.
 * Specifically for AP name, both full name string (the default mode, e.g. BYGTSG-4F-01) and
 * building name (e.g. BYGTSG) can be used.
 * If only building name is given, you can save processing time to declare this method with @full_apname param.
 * But for accuracy, the full AP name is preferred.
 *
 * @version 0.3
 * @author chenxm
 */
public class APTranslator {

    private static final String AP_BUILDING_DATABASE = "/apmap-utf8.yaml";
    private Map<String, Map<String, String>> APNameDB;
    private boolean full_apname = true;
    private Map<String, String> APBN_RealBN_Cache = new HashMap<String, String>();

    public APTranslator(){
        this(APTranslator.class.getResourceAsStream(AP_BUILDING_DATABASE), true);
    }

    public APTranslator(boolean full_apname){
        this(APTranslator.class.getResourceAsStream(AP_BUILDING_DATABASE), full_apname);
    }

    @SuppressWarnings("unchecked")
    public APTranslator(InputStream APDBYAML, boolean full_apname) {
        this.full_apname = full_apname;
        // Load yaml database
        Yaml yaml = new Yaml(new SafeConstructor());
        Map<String,Object> regexConfig = (Map<String,Object>) yaml.load(APDBYAML);
        APNameDB = (Map<String, Map<String, String>>) regexConfig.get("apprefix_sjtu");
    }

    public Map<String, String> parse(String APName){
        Map<String, String> result = null;
        if ( APName == null )
            return result;

        if ( full_apname )  { // Given full AP name string
            String[] parts = APName.split("-\\d+F-", 2);
            String buildName = parts[0];

            // Remove MH prefix
            if (buildName.startsWith("MH-"))
                buildName = buildName.substring(3, buildName.length());
            if (buildName.startsWith("MH"))
                buildName = buildName.substring(2, buildName.length());

            // Check cache first
            if ( APBN_RealBN_Cache.containsKey(buildName) ) { // Cache hit
                String cacheRealBN = APBN_RealBN_Cache.get(buildName);
                result = APNameDB.get(cacheRealBN);
            } else { // Cache miss
                if ( APNameDB.containsKey(buildName)) {
                    result = APNameDB.get(buildName);
                    APBN_RealBN_Cache.put(buildName, buildName);
                } else {
                    // Worst case; try to find its longest matched building name
                    String realBuildName = null;
                    for ( String BN : APNameDB.keySet())
                        if ( buildName.contains(BN) )
                            if ( realBuildName == null )
                                realBuildName = BN;
                            else if ( BN.length() > realBuildName.length() )
                                realBuildName = BN; // Get the longest match
                    if ( realBuildName != null ){
                        result = APNameDB.get(realBuildName);
                        // Cache the real building name
                        APBN_RealBN_Cache.put(buildName, realBuildName);
                    }
                }
            }
        } else { // Given build name, skip cache actions
            if ( APNameDB.containsKey(APName) ) // Have item
                result = APNameDB.get(APName);
        }

        return result;
    }
}