package es.hib.nlp.flexioner.es;

import java.io.IOException;
import java.io.InputStreamReader;
import java.io.LineNumberReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Properties;
import java.util.StringTokenizer;

/**
 * Spanish verbs flexioner.
 * 
 * @author jdelpeso
 *
 */
public class SpanishVerbFlexioner {

	// Table of models:
	// 	key: model name
	//  value: model
	private HashMap<String, Model> modelsByName = new HashMap<String, SpanishVerbFlexioner.Model>();

	// Table of irregular verbs:
	//	key: verb (inifinitive)
	//	value: Model
	private HashMap<String, Model> irregularVerbsNodels = new HashMap<String, Model>();
	
	private Model modelRegularAR;
	private Model modelRegularER;
	private Model modelRegularIR;
	
	/**
	 * 
	 * @throws IOException
	 */
	public SpanishVerbFlexioner() throws IOException {
		loadModels();
	}
	
	/**
	 * Load modesl into memory.
	 * 
	 * @throws IOException
	 */
	private void loadModels() throws IOException {
		// Load irregular verbs models.
		LineNumberReader in = new LineNumberReader(new InputStreamReader(this.getClass().getResourceAsStream("models")));
		String model_name;
		while ((model_name = in.readLine()) != null) {
			Model model = Model.loadModel(model_name);
			if (model != null) {
				modelsByName.put(model_name, model);
				// Add model to all corresponding irregular verbs.
				for (String irregular_verb: model.verbs)
					irregularVerbsNodels.put(irregular_verb, model);
			}
		}
		in.close();
		
		// Load regular verbs models.
		modelRegularAR = Model.loadModel("regular_ar");
		modelRegularER = Model.loadModel("regular_er");
		modelRegularIR = Model.loadModel("regular_ir");
	}

	/**
	 * Produces all the possible verb flexions for a given infinitive.
	 * 
	 * @param infinitive
	 * @return
	 */
	public ArrayList<String> getAllSimpleForms(String infinitive) {
		Model model = irregularVerbsNodels.get(infinitive);
		if (model != null) {
			// Irregular verb
			return model.getAllSimpleForms(infinitive);
		}
		if (infinitive.endsWith("ar"))
			return modelRegularAR.getAllSimpleForms(infinitive);
		if (infinitive.endsWith("er"))
			return modelRegularER.getAllSimpleForms(infinitive);
		if (infinitive.endsWith("ir"))
			return modelRegularIR.getAllSimpleForms(infinitive);
		return null;
	}
			
	/**
	 * Conjugation model
	 * 
	 * @author jdelpeso
	 *
	 */
	static class Model {
		String name;
		String suffix;
		ArrayList<String> flexing_suffixes = new ArrayList<String>();
		ArrayList<String> verbs = new ArrayList<String>();
		
		Model(String name) {
			this.name = name;
		}
		
		/**
		 * Get the root from an infinitive, according to current model.
		 * 
		 * @param infinitive
		 * @return
		 */
		String getRoot(String infinitive) {
			if (infinitive.endsWith(suffix))
				return infinitive.substring(0, infinitive.length() - suffix.length());
			return null;
		}

		ArrayList<String> getAllSimpleForms(String infinitive) {
			ArrayList<String> res = new ArrayList<String>();
			String root = getRoot(infinitive);
			for (String suffix: this.flexing_suffixes)
				res.add(root + suffix);
			return res;
		}
		
		/**
		 * Load a model from resource files.
		 * 
		 * @param modelName
		 * @return
		 * @throws IOException
		 */
		static Model loadModel(String modelName) throws IOException {
			Properties model_props = new Properties();
			model_props.load(SpanishVerbFlexioner.class.getResourceAsStream(modelName + ".props"));
			Model res = new Model(modelName);
			
			// Load model information
			res.suffix = model_props.getProperty("suffix");
			String verbs = model_props.getProperty("verbs");
			if (verbs != null) {
				StringTokenizer tok = new StringTokenizer(verbs, " \t,");
				while (tok.hasMoreTokens())
					res.verbs.add(tok.nextToken());
			}
			
			// Load suffixes
			LineNumberReader in = new LineNumberReader(new InputStreamReader(SpanishVerbFlexioner.class.getResourceAsStream(modelName + ".suffx")));
			String s;
			while ((s = in.readLine()) != null) {
				s = s.trim();
				if (s.length() > 0) { 
					if (!s.startsWith("#")){
						if (s.startsWith("@"))
							res.flexing_suffixes.add("");
						else
							res.flexing_suffixes.add(s);
					}
				}
			}
			in.close();
			
			return res;
		}
	}
	
	public static void main(String args[])  {
		try {
			String infinitives[] = {"abeldar", "cantar", "temer", "vivir"};
			SpanishVerbFlexioner flexioner = new SpanishVerbFlexioner();
			for (String v: infinitives) {
				System.out.println(v + " -> " + flexioner.getAllSimpleForms(v));
			}
		}
		catch (Exception e) {
			e.printStackTrace();
		}
		
	}

	
	
}
