from typing import List, Dict
from app.schemas.clinical import StandardDoseProtocol

CLINICAL_PROTOCOLS: Dict[str, List[StandardDoseProtocol]] = {
    # 1. Type 2 Diabetes
    "type_2_diabetes": [
        StandardDoseProtocol(
            generic_name="Metformin Hydrochloride",
            suggested_brand="Glycomet 500",
            brand_alternatives=["Bigomet 500", "Obimet 500", "Cetapin 500", "Glucophage 500"],
            adult_dosage="500 mg PO twice daily (titrate to 1000 mg twice daily, max 2000 mg/day)",
            pediatric_dosage="500 mg PO once daily (for adolescents >= 10 yrs)",
            route="Oral (PO)",
            frequency="Twice daily with meals",
            timing_instructions="Take with or immediately after meals to reduce gastrointestinal irritation.",
            renal_adjustment="Preserved if eGFR >= 45. Max 1000 mg/day if eGFR 30-44. Strictly contraindicated if eGFR < 30 mL/min/1.73m2.",
            common_strengths=["500 mg", "850 mg", "1000 mg", "SR 500 mg", "SR 1000 mg"]
        ),
        StandardDoseProtocol(
            generic_name="Regular Human Insulin",
            suggested_brand="Human Actrapid 40 IU/ml",
            brand_alternatives=["Huminsulin R 40IU", "Wosulin R 40IU", "Insugen R 40IU"],
            adult_dosage="10 - 20 units SC before meals (titrated to pre-meal capillary glucose)",
            pediatric_dosage="0.5 - 1.0 unit/kg/day total daily dose divided before meals",
            route="Subcutaneous (SC)",
            frequency="20-30 minutes before major meals",
            timing_instructions="Inject subcutaneously into abdominal wall, rotating injection sites. Ensure carbohydrate meal is consumed within 30 minutes.",
            renal_adjustment="Reduce dose by 25% if eGFR 15-50; reduce by 50% if eGFR < 15 mL/min due to prolonged insulin half-life.",
            common_strengths=["40 IU/ml vial", "100 IU/ml pen cartridge"]
        ),
        StandardDoseProtocol(
            generic_name="Glimepiride",
            suggested_brand="Amaryl 1mg / 2mg",
            brand_alternatives=["Zoryl 1mg/2mg", "Glimy 1mg", "Gemer 1mg", "Glimestar 1mg"],
            adult_dosage="1 mg to 2 mg PO once daily (max 4 mg/day)",
            route="Oral (PO)",
            frequency="Once daily with or immediately before breakfast",
            timing_instructions="Do not skip meals; risk of prolonged hypoglycemia if meals are missed.",
            renal_adjustment="Use with caution in CKD; switch to linagliptin or DPP4i if eGFR < 45 mL/min.",
            common_strengths=["1 mg", "2 mg", "3 mg", "4 mg"]
        ),
        StandardDoseProtocol(
            generic_name="Teneligliptin",
            suggested_brand="Ziten 20mg",
            brand_alternatives=["Tenglyn 20", "Dynaglipt 20", "Tenelimac 20", "Megagliptin 20"],
            adult_dosage="20 mg PO once daily (can increase to 40 mg if needed)",
            route="Oral (PO)",
            frequency="Once daily before or after breakfast",
            timing_instructions="Safe across all CKD stages without dose adjustment.",
            renal_adjustment="No renal dose adjustment required; suitable for patients with CKD stage 1 to 5.",
            common_strengths=["20 mg"]
        ),
        StandardDoseProtocol(
            generic_name="Dapagliflozin",
            suggested_brand="Forxiga 10mg",
            brand_alternatives=["Oxra 10mg", "Dapaone 10mg", "Gudapa 10mg", "Dapacip 10mg"],
            adult_dosage="10 mg PO once daily",
            route="Oral (PO)",
            frequency="Once daily in the morning with or without food",
            timing_instructions="Maintain adequate hydration to prevent volume depletion and urinary tract infections.",
            renal_adjustment="Cardio-renal benefit preserved down to eGFR 25 mL/min; glycemic efficacy diminishes if eGFR < 45.",
            common_strengths=["5 mg", "10 mg"]
        )
    ],

    # 2. Essential Hypertension
    "essential_hypertension": [
        StandardDoseProtocol(
            generic_name="Amlodipine Besylate",
            suggested_brand="Amlodac 5",
            brand_alternatives=["Amlopres 5", "Stamlo 5", "Amlovas 5", "Camlo 5"],
            adult_dosage="5 mg PO once daily (titrate to 10 mg after 2-4 weeks if target BP not reached)",
            route="Oral (PO)",
            frequency="Once daily (morning or bedtime)",
            timing_instructions="May be taken with or without food. Monitor for ankle edema at 10 mg dose.",
            renal_adjustment="No dosage reduction required in renal impairment.",
            common_strengths=["2.5 mg", "5 mg", "10 mg"]
        ),
        StandardDoseProtocol(
            generic_name="Telmisartan",
            suggested_brand="Telma 40",
            brand_alternatives=["Telmikind 40", "Creser 40", "Telsartan 40", "Arbitel 40"],
            adult_dosage="40 mg PO once daily (can increase to 80 mg once daily)",
            route="Oral (PO)",
            frequency="Once daily at the same time each day",
            timing_instructions="Long 24-hour half life provides consistent nocturnal BP control. Monitor potassium and creatinine.",
            renal_adjustment="No initial dosage adjustment for renal impairment. Monitor serum potassium in severe CKD.",
            common_strengths=["20 mg", "40 mg", "80 mg"]
        ),
        StandardDoseProtocol(
            generic_name="Lisinopril",
            suggested_brand="Lipril 5",
            brand_alternatives=["Listril 5", "Zestril 5", "Lisinace 5"],
            adult_dosage="5 mg to 10 mg PO once daily (max 40 mg/day)",
            route="Oral (PO)",
            frequency="Once daily in the morning",
            timing_instructions="STRICT CONTRAINDICATION in pregnancy (fetotoxicity) and bilateral renal artery stenosis. Withhold if Potassium > 5.5 mEq/L.",
            renal_adjustment="Reduce initial dose to 2.5 mg if eGFR < 30 mL/min/1.73m2.",
            common_strengths=["2.5 mg", "5 mg", "10 mg", "20 mg"]
        ),
        StandardDoseProtocol(
            generic_name="Metoprolol Succinate (ER)",
            suggested_brand="Betaloc 25 / 50",
            brand_alternatives=["Metolar 25/50", "Starpress XL 25/50", "ProloMet XL 25/50"],
            adult_dosage="25 mg to 50 mg PO once daily (titrate to 100 mg for CAD/tachycardia)",
            route="Oral (PO)",
            frequency="Once daily with food",
            timing_instructions="Swallow extended-release tablet whole; do not crush or chew. Take with meals.",
            renal_adjustment="No dose adjustment in renal impairment.",
            common_strengths=["12.5 mg", "25 mg", "50 mg", "100 mg"]
        )
    ],

    # 3. Congestive Heart Failure
    "heart_failure": [
        StandardDoseProtocol(
            generic_name="Furosemide",
            suggested_brand="Lasix 40mg",
            brand_alternatives=["Frusenex 40", "Furesis 40", "Salinex 40"],
            adult_dosage="20 mg to 40 mg IV/PO once or twice daily (titrated to maintain euvolemia)",
            route="Oral (PO) or Intravenous (IV)",
            frequency="Once or twice daily (take morning and early afternoon to prevent nocturia)",
            timing_instructions="Monitor daily weight, serum potassium, and renal panel. Replace potassium if < 4.0 mEq/L.",
            renal_adjustment="Higher doses (80-160 mg) required in advanced renal impairment to achieve diuresis.",
            common_strengths=["20 mg", "40 mg", "Injection 10 mg/ml"]
        ),
        StandardDoseProtocol(
            generic_name="Spironolactone",
            suggested_brand="Aldactone 25",
            brand_alternatives=["Spiroctan 25", "Aldoprime 25", "Cardactone 25"],
            adult_dosage="25 mg PO once daily (titrate to 50 mg if potassium permits)",
            route="Oral (PO)",
            frequency="Once daily with breakfast",
            timing_instructions="MANDATORY SAFETY GATE: Withhold if baseline Serum Potassium > 5.0 mEq/L or eGFR < 30 mL/min.",
            renal_adjustment="Contraindicated if eGFR < 30 mL/min/1.73m2 due to high hyperkalemia fatality risk.",
            common_strengths=["25 mg", "50 mg", "100 mg"]
        ),
        StandardDoseProtocol(
            generic_name="Ramipril",
            suggested_brand="Cardace 2.5 / 5",
            brand_alternatives=["Hopace 2.5", "Ramistar 2.5/5", "Corpril 2.5"],
            adult_dosage="2.5 mg PO once daily (titrate to target dose of 10 mg/day)",
            route="Oral (PO)",
            frequency="Once daily",
            timing_instructions="Mortality reduction in HFrEF. Check creatinine and potassium at baseline and 1-2 weeks after titration.",
            renal_adjustment="Reduce starting dose to 1.25 mg if eGFR < 30 mL/min.",
            common_strengths=["1.25 mg", "2.5 mg", "5 mg", "10 mg"]
        )
    ],

    # 4. Bronchial Asthma
    "asthma": [
        StandardDoseProtocol(
            generic_name="Budesonide + Formoterol Inhaler",
            suggested_brand="Foracort 200 Inhaler",
            brand_alternatives=["Budetrol 200", "Symbicort 160/4.5", "Fomtide 200"],
            adult_dosage="1 - 2 puffs twice daily (MDI with spacer) plus 1 puff as-needed for relief (MART regimen)",
            pediatric_dosage="Foracort 100 Inhaler 1 puff twice daily for children 6-11 yrs",
            route="Inhalation (MDI with spacer)",
            frequency="Twice daily (morning and evening) + PRN relief",
            timing_instructions="Always rinse mouth and gargle with plain water after inhalation to prevent oral candidiasis.",
            renal_adjustment="No renal dose adjustment required.",
            common_strengths=["100/6 mcg", "200/6 mcg", "400/6 mcg"]
        ),
        StandardDoseProtocol(
            generic_name="Salbutamol (Albuterol)",
            suggested_brand="Asthalin 100mcg Inhaler",
            brand_alternatives=["Ventorlin Inhaler", "Aerocort Inhaler", "Asthavent"],
            adult_dosage="100 - 200 mcg (1 to 2 puffs) as-needed for acute bronchospasm",
            pediatric_dosage="100 mcg (1 puff) via spacer for acute relief",
            route="Inhalation",
            frequency="Every 4-6 hours as-needed (max 8 puffs/day)",
            timing_instructions="Reliever only. Per GINA / ICMR guidelines, Salbutamol monotherapy without inhaled steroids is unsafe.",
            renal_adjustment="No dose adjustment required.",
            common_strengths=["100 mcg per metered dose"]
        ),
        StandardDoseProtocol(
            generic_name="Montelukast Sodium",
            suggested_brand="Montair 10",
            brand_alternatives=["Romilast 10", "Telekast 10", "Montek 10"],
            adult_dosage="10 mg PO once daily at bedtime",
            pediatric_dosage="4 mg (2-5 yrs), 5 mg (6-14 yrs) chewable tablet once daily at bedtime",
            route="Oral (PO)",
            frequency="Once daily at bedtime",
            timing_instructions="Take at bedtime. Effective add-on controller for nocturnal asthma and allergic rhinitis.",
            renal_adjustment="No renal dose adjustment required.",
            common_strengths=["4 mg chewable", "5 mg chewable", "10 mg tablet"]
        )
    ],

    # 5. GERD & Peptic Ulcer Disease
    "gerd": [
        StandardDoseProtocol(
            generic_name="Pantoprazole Sodium",
            suggested_brand="Pan 40",
            brand_alternatives=["Pantocid 40", "Pantodac 40", "Nupenta 40", "Protera 40"],
            adult_dosage="40 mg PO once daily for 4 to 8 weeks",
            route="Oral (PO)",
            frequency="Once daily in the morning",
            timing_instructions="Must be taken 30 to 60 minutes BEFORE breakfast with plain water for optimal parietal cell proton pump inhibition.",
            renal_adjustment="No dosage reduction required in renal insufficiency.",
            common_strengths=["20 mg", "40 mg", "IV Injection 40 mg"]
        ),
        StandardDoseProtocol(
            generic_name="Rabeprazole Sodium",
            suggested_brand="Rablet 20",
            brand_alternatives=["Happi 20", "Cyra 20", "Parit 20", "Razo 20"],
            adult_dosage="20 mg PO once daily before breakfast",
            route="Oral (PO)",
            frequency="Once daily 30 minutes before morning meal",
            timing_instructions="Rapid onset PPI providing immediate daytime and nocturnal acid suppression.",
            renal_adjustment="No renal dose adjustment required.",
            common_strengths=["10 mg", "20 mg"]
        ),
        StandardDoseProtocol(
            generic_name="Magaldrate + Simethicone Oral Suspension",
            suggested_brand="Gelusil MPS Syrup",
            brand_alternatives=["Mucaine Gel", "Digene Gel", "Relacer Gel"],
            adult_dosage="10 ml to 15 ml orally as needed after meals and at bedtime",
            route="Oral (PO)",
            frequency="3 to 4 times daily, 1 hour after meals and at bedtime",
            timing_instructions="Shake well before use. Do not take within 2 hours of oral antibiotics (fluoroquinolones, tetracyclines) due to chelation.",
            renal_adjustment="Avoid long-term high dose in severe renal impairment (magnesium accumulation risk).",
            common_strengths=["200 ml suspension bottle"]
        )
    ],

    # 6. Urinary Tract Infection (Acute Cystitis)
    "urinary_tract_infection": [
        StandardDoseProtocol(
            generic_name="Nitrofurantoin (Macrobid / Dual Release)",
            suggested_brand="Martifur 100mg",
            brand_alternatives=["Niftran 100", "Uribid 100", "Furadantin 100"],
            adult_dosage="100 mg PO twice daily for 5 to 7 days",
            route="Oral (PO)",
            frequency="Twice daily with meals (every 12 hours)",
            timing_instructions="Must be taken with food or milk to enhance bioavailability and avoid nausea. Urine will turn brownish/yellow.",
            renal_adjustment="CONTRAINDICATED if eGFR < 30 mL/min/1.73m2 (sub-therapeutic urinary concentration and risk of peripheral neuropathy).",
            common_strengths=["100 mg sustained release tablet"]
        ),
        StandardDoseProtocol(
            generic_name="Fosfomycin Trometamol",
            suggested_brand="Monurol 3g Sachet",
            brand_alternatives=["Fosfocin 3g", "Fosfocil 3g", "Crani-Fos 3g"],
            adult_dosage="3 g single oral dose dissolved in water",
            route="Oral (PO)",
            frequency="Single one-time dose",
            timing_instructions="Empty bladder, dissolve entire 3g sachet in 100ml plain room-temperature water, drink immediately on empty stomach at bedtime.",
            renal_adjustment="Not recommended if eGFR < 10 mL/min.",
            common_strengths=["3 g oral sachet"]
        ),
        StandardDoseProtocol(
            generic_name="Ciprofloxacin Hydrochloride",
            suggested_brand="Ciplox 500",
            brand_alternatives=["Cifran 500", "Ciprobid 500", "Microflox 500"],
            adult_dosage="500 mg PO twice daily for 5 to 7 days (complicated UTI / pyelonephritis)",
            route="Oral (PO)",
            frequency="Twice daily",
            timing_instructions="Do not take with dairy products, calcium, or antacids. Maintain high fluid intake (2-3 L/day).",
            renal_adjustment="Reduce dose to 250-500 mg once daily if eGFR < 30 mL/min.",
            common_strengths=["250 mg", "500 mg", "750 mg"]
        )
    ],

    # 7. Dyslipidemia / Cardiovascular Risk
    "dyslipidemia": [
        StandardDoseProtocol(
            generic_name="Atorvastatin Calcium",
            suggested_brand="Atorva 20",
            brand_alternatives=["Storvas 20", "Lipikind 20", "Atocor 20", "Tonact 20"],
            adult_dosage="20 mg to 40 mg PO once daily at bedtime (max 80 mg/day for ACS)",
            route="Oral (PO)",
            frequency="Once daily at bedtime",
            timing_instructions="Take at night. Baseline liver function tests recommended. Discontinue if unexplained severe muscle aches occur.",
            renal_adjustment="No dosage adjustment needed for renal impairment.",
            common_strengths=["10 mg", "20 mg", "40 mg", "80 mg"]
        ),
        StandardDoseProtocol(
            generic_name="Rosuvastatin Calcium",
            suggested_brand="Rosuvas 10",
            brand_alternatives=["Rozavel 10", "Roseday 10", "Crestor 10", "Novastat 10"],
            adult_dosage="10 mg to 20 mg PO once daily (start at 5-10 mg in elderly or Asian patients)",
            route="Oral (PO)",
            frequency="Once daily at bedtime",
            timing_instructions="High-potency statin providing >50% LDL-C reduction. Can be taken with or without food.",
            renal_adjustment="Start with 5 mg once daily in patients with severe renal impairment (eGFR < 30 mL/min); max 10 mg/day.",
            common_strengths=["5 mg", "10 mg", "20 mg", "40 mg"]
        )
    ],

    # 8. Hypothyroidism
    "hypothyroidism": [
        StandardDoseProtocol(
            generic_name="Levothyroxine Sodium",
            suggested_brand="Thyronorm 50mcg",
            brand_alternatives=["Eltroxin 50mcg", "Thyrox 50mcg", "Utirox 50mcg"],
            adult_dosage="25 mcg to 100 mcg PO once daily (full replacement dose ~1.6 mcg/kg/day)",
            route="Oral (PO)",
            frequency="Once daily first thing in the morning",
            timing_instructions="MANDATORY: Take on an empty stomach with plain water at least 30 to 60 minutes before breakfast, coffee, or calcium/iron supplements.",
            renal_adjustment="No renal dose adjustment. Recheck serum TSH every 6 to 8 weeks until euthyroid.",
            common_strengths=["12.5 mcg", "25 mcg", "50 mcg", "75 mcg", "88 mcg", "100 mcg", "125 mcg", "150 mcg"]
        )
    ],

    # 9. Acute Gastroenteritis & Diarrheal Illness
    "acute_gastroenteritis": [
        StandardDoseProtocol(
            generic_name="Oral Rehydration Salts (WHO Formula)",
            suggested_brand="Electral Sachet 21.8g",
            brand_alternatives=["Prolyte ORS Sachet", "Walyte ORS", "Electrobion"],
            adult_dosage="1 sachet dissolved in 1 liter clean water, drink 200-400 ml after each loose stool (2-3 L/day)",
            pediatric_dosage="50-100 ml after each loose stool for children < 2 yrs; 100-200 ml for children > 2 yrs",
            route="Oral (PO)",
            frequency="Sip continuously throughout the day",
            timing_instructions="Do not boil reconstituted solution. Discard unused solution after 24 hours.",
            renal_adjustment="Monitor volume and electrolytes carefully in pre-existing CKD.",
            common_strengths=["21.8 g sachet (makes 1 liter)"]
        ),
        StandardDoseProtocol(
            generic_name="Zinc Sulfate Monohydrate",
            suggested_brand="Zinconia 20",
            brand_alternatives=["Zincovit Tablet", "Zinconia Syrup", "Nu-Zinc"],
            adult_dosage="20 mg PO once daily for 14 days",
            pediatric_dosage="10 mg daily (< 6 months); 20 mg daily (>= 6 months) for 14 days",
            route="Oral (PO)",
            frequency="Once daily for 14 consecutive days",
            timing_instructions="Complete full 14-day course even after diarrhea ceases to restore intestinal mucosal integrity.",
            renal_adjustment="No adjustment required.",
            common_strengths=["20 mg tablet", "20 mg/5ml syrup"]
        ),
        StandardDoseProtocol(
            generic_name="Ofloxacin + Ornidazole",
            suggested_brand="O2 Tablet",
            brand_alternatives=["Zenflox-OZ", "Ornof Tablet", "Oflomac-OZ"],
            adult_dosage="Ofloxacin 200mg + Ornidazole 500mg PO twice daily for 3 to 5 days",
            route="Oral (PO)",
            frequency="Twice daily after meals",
            timing_instructions="Indicated ONLY for acute invasive diarrhea with visible blood, mucus, or high fever. Avoid alcohol during therapy (disulfiram-like reaction).",
            renal_adjustment="Reduce dose by 50% if eGFR < 30 mL/min.",
            common_strengths=["200 mg / 500 mg combination tablet"]
        ),
        StandardDoseProtocol(
            generic_name="Racecadotril",
            suggested_brand="Redotil 100",
            brand_alternatives=["Zedott 100", "Enuff 100", "Cadotril 100"],
            adult_dosage="100 mg PO three times daily before meals until normal stool (max 7 days)",
            pediatric_dosage="1.5 mg/kg PO three times daily (sachet in food/water)",
            route="Oral (PO)",
            frequency="Three times daily before main meals",
            timing_instructions="Enkephalinase inhibitor that reduces intestinal hypersecretion without slowing bowel motility.",
            renal_adjustment="No renal dose adjustment required.",
            common_strengths=["100 mg capsule", "10 mg / 30 mg pediatric sachet"]
        )
    ],

    # 10. Migraine & Tension Headache
    "migraine": [
        StandardDoseProtocol(
            generic_name="Naproxen Sodium + Domperidone",
            suggested_brand="Napra-D 500",
            brand_alternatives=["Xenobid-D 500", "Domstal-NP", "Naprosyn-D"],
            adult_dosage="Naproxen 500mg + Domperidone 10mg PO stat at onset of migraine headache",
            route="Oral (PO)",
            frequency="At headache onset; can repeat once after 2 hours if required (max 2 tabs/day)",
            timing_instructions="Take with a full glass of water and food to prevent gastric irritation. Domperidone prevents migraine-associated gastric stasis and nausea.",
            renal_adjustment="Contraindicated in severe renal failure (eGFR < 30 mL/min).",
            common_strengths=["500 mg / 10 mg tablet"]
        ),
        StandardDoseProtocol(
            generic_name="Sumatriptan Succinate",
            suggested_brand="Suminat 50",
            brand_alternatives=["Headset 50", "Migriptan 50", "Sumitrex 50"],
            adult_dosage="50 mg to 100 mg PO stat at onset of acute migraine attack",
            route="Oral (PO)",
            frequency="At onset; may repeat once after 2 hours if headache recurs (max 200 mg in 24h)",
            timing_instructions="STRICT CONTRAINDICATION: Coronary artery disease, uncontrolled hypertension, history of stroke/TIA due to vasoconstrictive properties.",
            renal_adjustment="No dosage reduction required in renal impairment.",
            common_strengths=["25 mg", "50 mg", "100 mg"]
        ),
        StandardDoseProtocol(
            generic_name="Propranolol Hydrochloride (Prophylaxis)",
            suggested_brand="Ciplar 40",
            brand_alternatives=["Inderal 40", "Betacap TR 40", "Provanol 40"],
            adult_dosage="40 mg PO once daily (titrate to 40 mg twice daily for preventive therapy)",
            route="Oral (PO)",
            frequency="Daily for migraine prophylaxis (minimum 3 months trial)",
            timing_instructions="STRICT CONTRAINDICATION in Bronchial Asthma / COPD (risk of fatal bronchospasm) and severe bradycardia.",
            renal_adjustment="Use with caution in renal failure.",
            common_strengths=["10 mg", "20 mg", "40 mg", "80 mg ER"]
        )
    ],

    # 11. Allergic Rhinitis & Urticaria
    "allergic_rhinitis_urticaria": [
        StandardDoseProtocol(
            generic_name="Bilastine",
            suggested_brand="Bilaxten 20",
            brand_alternatives=["Bilashine 20", "Blisto 20", "Bilanta 20", "Bilasure 20"],
            adult_dosage="20 mg PO once daily",
            route="Oral (PO)",
            frequency="Once daily",
            timing_instructions="MANDATORY: Must be taken on an empty stomach (1 hour before or 2 hours after food or fruit juices like grapefruit/orange). Non-sedating.",
            renal_adjustment="No dose adjustment required in renal impairment.",
            common_strengths=["20 mg tablet"]
        ),
        StandardDoseProtocol(
            generic_name="Levocetirizine + Montelukast",
            suggested_brand="Montair-LC",
            brand_alternatives=["Telekast-L", "Montek-LC", "Levocet-M", "Romilast-L"],
            adult_dosage="Levocetirizine 5mg + Montelukast 10mg PO once daily at bedtime",
            route="Oral (PO)",
            frequency="Once daily at bedtime",
            timing_instructions="Provides dual histamine H1 and cysteinyl leukotriene receptor blockade for allergic rhinitis and chronic idiopathic urticaria.",
            renal_adjustment="Dose reduction of levocetirizine to alternate days if eGFR 30-50 mL/min.",
            common_strengths=["5 mg / 10 mg tablet", "Kid syrup (2.5mg / 4mg)"]
        ),
        StandardDoseProtocol(
            generic_name="Fluticasone Furoate Nasal Spray",
            suggested_brand="Flomist Nasal Spray",
            brand_alternatives=["Furamist Nasal Spray", "Fluticone", "Avamys"],
            adult_dosage="2 sprays (27.5 mcg/spray) into each nostril once daily, reducing to 1 spray per nostril once controlled",
            route="Nasal Spray",
            frequency="Once daily in the morning",
            timing_instructions="Blow nose gently before application. Shake bottle well. Point spray away from nasal septum.",
            renal_adjustment="No renal dose adjustment required.",
            common_strengths=["27.5 mcg per actuation bottle"]
        )
    ],

    # 12. COPD (Chronic Obstructive Pulmonary Disease)
    "copd": [
        StandardDoseProtocol(
            generic_name="Tiotropium + Formoterol Inhaler",
            suggested_brand="Tiova-F Inhaler",
            brand_alternatives=["Duova Inhaler", "Tioform Inhaler", "Aerotrop-F"],
            adult_dosage="1 puff (Tiotropium 18mcg + Formoterol 12mcg) twice daily via DPI / MDI with spacer",
            route="Inhalation",
            frequency="Twice daily (morning and evening)",
            timing_instructions="Dual LAMA + LABA bronchodilation. Rinse mouth after use. Monitor for dry mouth and urinary retention in BPH.",
            renal_adjustment="Monitor closely if eGFR < 30 mL/min (primarily renal excretion of tiotropium).",
            common_strengths=["18 mcg / 12 mcg rotacaps / inhaler"]
        ),
        StandardDoseProtocol(
            generic_name="N-Acetylcysteine (Mucolytic)",
            suggested_brand="Mucosef 600",
            brand_alternatives=["Nacfil 600", "Mucomelt 600", "Fluimucil 600"],
            adult_dosage="600 mg PO twice daily effervescent tablet dissolved in water",
            route="Oral (PO)",
            frequency="Twice daily after meals",
            timing_instructions="Dissolve completely in half a glass of room temperature water and drink immediately. Reduces COPD exacerbation frequency.",
            renal_adjustment="No renal dose adjustment required.",
            common_strengths=["600 mg effervescent tablet"]
        )
    ],

    # 13. Dengue Fever
    "dengue": [
        StandardDoseProtocol(
            generic_name="Paracetamol (Acetaminophen)",
            suggested_brand="Dolo 650",
            brand_alternatives=["Calpol 500/650", "Crocin 650", "Pacimol 650"],
            adult_dosage="500 mg to 650 mg PO every 6 to 8 hours PRN for fever > 100°F (max 3000 mg/day)",
            pediatric_dosage="10 to 15 mg/kg PO every 6 hours PRN (max 60 mg/kg/day)",
            route="Oral (PO)",
            frequency="Every 6-8 hours as needed",
            timing_instructions="STRICT CONTRAINDICATION: NSAIDs (Ibuprofen, Diclofenac, Mefenamic Acid) and Aspirin are strictly barred due to catastrophic platelet inhibition and hemorrhagic gastritis.",
            renal_adjustment="Dosing interval q8h if eGFR < 50 mL/min.",
            common_strengths=["500 mg", "650 mg", "120 mg/5ml syrup", "250 mg/5ml syrup"]
        ),
        StandardDoseProtocol(
            generic_name="Crystalloid Fluid Resuscitation (Normal Saline 0.9% / Ringer Lactate)",
            suggested_brand="Normal Saline 0.9% IV Infusion",
            brand_alternatives=["Ringer Lactate Infusion", "Isolyte-P Infusion"],
            adult_dosage="5 to 7 ml/kg/hr for 1-2 hours in warning signs phase, step down to 3-5 ml/kg/hr and 2-3 ml/kg/hr",
            route="Intravenous (IV)",
            frequency="Continuous guided IV infusion with hematocrit and urine output monitoring",
            timing_instructions="Titrate to target urine output >= 0.5 ml/kg/hr. Avoid fluid overload in defervescent phase.",
            renal_adjustment="Careful volumetric rate titration with central venous monitoring if renal or cardiac failure.",
            common_strengths=["500 ml IV bottle", "1000 ml IV bottle"]
        )
    ],

    # 14. Malaria
    "malaria": [
        StandardDoseProtocol(
            generic_name="Artemether + Lumefantrine (ACT)",
            suggested_brand="Coartem Tablet",
            brand_alternatives=["Falcigo-Plus", "Lumart Tablet", "Arte Plus"],
            adult_dosage="4 tablets (Artemether 20mg + Lumefantrine 120mg per tab) at 0h, 8h, 24h, 36h, 48h, and 60h (total 24 tabs)",
            route="Oral (PO)",
            frequency="Specific 6-dose ACT schedule over 3 days",
            timing_instructions="MANDATORY: Must be taken with food or milk; fat greatly enhances lumefantrine oral absorption.",
            renal_adjustment="No dosage adjustment needed for renal impairment.",
            common_strengths=["20 mg / 120 mg tablet"]
        ),
        StandardDoseProtocol(
            generic_name="Chloroquine Phosphate (for P. vivax)",
            suggested_brand="Lariago 250mg",
            brand_alternatives=["Resochin 250mg", "Cloquin 250mg"],
            adult_dosage="600 mg base (4 tabs of 250mg) stat, 300 mg base at 6h, 24h, and 48h (total 1500 mg base over 3 days)",
            route="Oral (PO)",
            frequency="Day 1: 0h & 6h; Day 2: 24h; Day 3: 48h",
            timing_instructions="Standard first-line regimen for chloroquine-sensitive Plasmodium vivax malaria.",
            renal_adjustment="Reduce dose by 50% if eGFR < 10 mL/min.",
            common_strengths=["250 mg tablet (150 mg chloroquine base)"]
        ),
        StandardDoseProtocol(
            generic_name="Primaquine Phosphate (Anti-Relapse Radical Cure)",
            suggested_brand="Malirid 15mg",
            brand_alternatives=["Primacip 15mg", "PMQ 15mg"],
            adult_dosage="15 mg PO once daily for 14 consecutive days (for P. vivax hypnozoite radical cure)",
            route="Oral (PO)",
            frequency="Once daily with food for 14 days",
            timing_instructions="MANDATORY SAFETY GATE: Must test G6PD activity prior to prescribing. STRICTLY CONTRAINDICATED in G6PD deficiency (fatal acute hemolytic anemia) and in pregnancy.",
            renal_adjustment="Use with caution in severe renal disease.",
            common_strengths=["7.5 mg", "15 mg"]
        )
    ],

    # 15. Tuberculosis
    "tuberculosis": [
        StandardDoseProtocol(
            generic_name="Fixed-Dose Combination 4-FDC (HRZE: Isoniazid + Rifampicin + Pyrazinamide + Ethambutol)",
            suggested_brand="Akurit-4 Tablet",
            brand_alternatives=["Forecox Tablet", "Macleods 4-FDC", "Rimactazid-4"],
            adult_dosage="Daily weight-band dosing: 3 tablets (35-49kg), 4 tablets (50-64kg), 5 tablets (>=65kg) for 2 months",
            route="Oral (PO)",
            frequency="Once daily on an empty stomach for 2 months (Intensive Phase)",
            timing_instructions="Take together on empty stomach 1 hour before breakfast. Urine and sweat will turn harmless reddish-orange (Rifampicin). Baseline LFTs and monthly monitoring required.",
            renal_adjustment="In severe renal failure (CrCl < 30), split into individual drugs to reduce Pyrazinamide and Ethambutol frequency to three times weekly.",
            common_strengths=["H 75mg + R 150mg + Z 400mg + E 275mg fixed-dose tablet"]
        ),
        StandardDoseProtocol(
            generic_name="Pyridoxine Hydrochloride (Vitamin B6)",
            suggested_brand="Benalgis 40mg",
            brand_alternatives=["B-Long 50mg", "Pyridox 40mg"],
            adult_dosage="20 mg to 40 mg PO once daily alongside anti-tubercular therapy",
            route="Oral (PO)",
            frequency="Once daily",
            timing_instructions="Mandatory co-prescription with Isoniazid (INH) to prevent peripheral neuropathy, especially in diabetic and malnourished patients.",
            renal_adjustment="No renal dose adjustment required.",
            common_strengths=["40 mg", "50 mg", "100 mg"]
        )
    ]
}

def get_additional_diseases():
    from app.evidence.disease_catalogue import DiseaseCoverageEntry
    return {
        "gerd": DiseaseCoverageEntry(
            disease_id="gerd",
            disease_name="GERD & Peptic Ulcer Disease (Acid Peptic Disorders)",
            category="Gastrointestinal",
            icd_10_codes=["K21.9", "K25.9", "K29.7"],
            evidence_coverage="Active (ICMR Standard Treatment Workflow for Dyspepsia and Gastroesophageal Reflux Disease, 2022; ACG 2022 Guidelines for Diagnosis and Management of GERD).",
            evidence_sources=["ICMR_GERD_2022", "ACG_GERD_2022"],
            medicine_selection_coverage="Proton pump inhibitors: Pantoprazole / Rabeprazole (first-line); Antacid mucosal protectants (Magaldrate + Simethicone); Prokinetics (Itopride / Levosulpiride) for delayed gastric emptying.",
            candidate_medicines=["Pantoprazole Sodium PO", "Rabeprazole Sodium PO", "Magaldrate + Simethicone Gel", "Itopride Hydrochloride PO"],
            dose_method_coverage="Pantoprazole 40 mg PO OD 30-60 min before breakfast x 4-8 weeks. Rabeprazole 20 mg PO OD before breakfast. Antacid gel 10-15 ml 1h post-prandial prn.",
            dose_method_type="GUIDELINE_ALGORITHM",
            model_evaluation_status="ICMR 2022 Guideline Protocol with lifestyle acid-suppression gating.",
            supported_age_group="Adults and Adolescents (>= 12 yrs)",
            supported_subtypes=["Non-Erosive Reflux Disease (NERD)", "Erosive Esophagitis", "Duodenal / Gastric Ulcer", "Functional Dyspepsia"],
            supported_severity=["Mild", "Moderate", "Severe"],
            supported_care_setting=["Primary Care Clinic / Outpatient Gastroenterology"],
            required_inputs=["age", "weight_kg"],
            missing_data_requirements=["Duration of heartburn/regurgitation", "Alarm features (dysphagia, hematemesis, unintentional weight loss, melena)", "H. pylori stool antigen or UBT status if peptic ulcer suspected"],
            subtype_prompt_guidance="Evaluate for red-flag alarm symptoms (dysphagia, GI bleeding, anemia) requiring urgent upper GI endoscopy.",
            exclusions=["Active upper GI hemorrhage (requires urgent IV PPI infusion and endoscopic hemostasis)", "Esophageal malignancy"],
            is_dose_model_ready=True,
            treatment_protocols=CLINICAL_PROTOCOLS.get("gerd", [])
        ),

        "urinary_tract_infection": DiseaseCoverageEntry(
            disease_id="urinary_tract_infection",
            disease_name="Urinary Tract Infection (Acute Uncomplicated Cystitis)",
            category="Renal & Urological / Infectious",
            icd_10_codes=["N39.0", "N30.0"],
            evidence_coverage="Active (ICMR Treatment Guidelines for Antimicrobial Use in Common Syndromes: Urinary Tract Infections, 2022; IDSA Clinical Practice Guidelines for Acute Uncomplicated Cystitis).",
            evidence_sources=["ICMR_AMR_UTI_2022", "IDSA_UTI_2021"],
            medicine_selection_coverage="First-line oral antimicrobials: Nitrofurantoin (Macrobid); Fosfomycin Trometamol; Ciprofloxacin / Levofloxacin (second-line for complicated/pyelonephritis). Urine alkalinisers (Disodium hydrogen citrate) for dysuria.",
            candidate_medicines=["Nitrofurantoin 100mg PO", "Fosfomycin Trometamol 3g PO", "Ciprofloxacin 500mg PO", "Disodium Hydrogen Citrate Syrup"],
            dose_method_coverage="Nitrofurantoin 100 mg PO BD with food x 5-7 days. Fosfomycin 3 g single oral dose sachet. Ciprofloxacin 500 mg PO BD x 5-7 days (pyelonephritis).",
            dose_method_type="GUIDELINE_ALGORITHM",
            model_evaluation_status="ICMR Antimicrobial Stewardship Protocol with strict Renal Clearance Gating.",
            supported_age_group="Adults (>= 18 yrs), Non-pregnant females, Elderly",
            supported_subtypes=["Acute Uncomplicated Cystitis", "Recurrent Cystitis", "Catheter-Associated UTI", "Acute Pyelonephritis"],
            supported_severity=["Mild / Uncomplicated", "Moderate", "Complicated / Febrile"],
            supported_care_setting=["Outpatient Primary Care / Urgent Care Clinic"],
            required_inputs=["age", "gender", "weight_kg", "creatinine"],
            missing_data_requirements=["Serum creatinine / eGFR (mandatory for Nitrofurantoin)", "Pregnancy status", "Urine routine microscopy (pus cells, nitrites)", "Flank pain / high fever (to rule out pyelonephritis)"],
            subtype_prompt_guidance="Differentiate lower UTI (dysuria, urgency without fever) from upper UTI (flank pain, costovertebral tenderness, fever > 101°F).",
            exclusions=["Nitrofurantoin is strictly contraindicated if eGFR < 30 mL/min/1.73m2 due to lack of urinary concentration and peripheral neuropathy risk", "Male UTI (considered complicated, requires 10-14 days treatment)", "Pregnancy near term (contraindicates Nitrofurantoin due to risk of neonatal hemolysis)"],
            is_dose_model_ready=True,
            treatment_protocols=CLINICAL_PROTOCOLS.get("urinary_tract_infection", [])
        ),

        "dyslipidemia": DiseaseCoverageEntry(
            disease_id="dyslipidemia",
            disease_name="Dyslipidemia & Cardiovascular Atherosclerotic Risk",
            category="Cardiovascular / Metabolic",
            icd_10_codes=["E78.0", "E78.2", "E78.5"],
            evidence_coverage="Active (Lipid Association of India Expert Consensus on Management of Dyslipidemia, 2023; ACC/AHA Multi-Society Guideline on the Management of Blood Cholesterol).",
            evidence_sources=["LAI_CONSENSUS_2023", "ACC_AHA_LIPIDS_2022"],
            medicine_selection_coverage="HMG-CoA reductase inhibitors: Atorvastatin (high/moderate intensity); Rosuvastatin; Ezetimibe (cholesterol absorption inhibitor add-on).",
            candidate_medicines=["Atorvastatin Calcium PO", "Rosuvastatin Calcium PO", "Ezetimibe PO", "Fenofibrate PO (for high triglycerides)"],
            dose_method_coverage="Atorvastatin 20-40 mg PO OD at bedtime (target LDL-C < 70 mg/dL or < 55 mg/dL in very high risk). Rosuvastatin 10-20 mg PO OD at bedtime.",
            dose_method_type="GUIDELINE_ALGORITHM",
            model_evaluation_status="Lipid Association of India 2023 Risk-Stratified Guideline Protocol.",
            supported_age_group="Adults (>= 20 yrs)",
            supported_subtypes=["Primary Hypercholesterolemia", "Mixed Dyslipidemia", "Diabetic Dyslipidemia", "Familial Hypercholesterolemia"],
            supported_severity=["Moderate Risk", "High Risk", "Very High / Extreme Risk (Known CAD/Stroke)"],
            supported_care_setting=["Preventive Cardiology / Outpatient General Medicine"],
            required_inputs=["age", "weight_kg"],
            missing_data_requirements=["Fasting Lipid Profile (Total Cholesterol, LDL-C, HDL-C, Triglycerides)", "Baseline Liver Function Tests (ALT/AST)", "Prior cardiovascular history (ACS, PCI, CABG, Ischemic Stroke)"],
            subtype_prompt_guidance="Classify patient risk category (Primary Prevention vs Secondary Prevention with known Atherosclerotic Cardiovascular Disease).",
            exclusions=["Active decompensated liver disease (acute hepatitis, unexplained persistent transaminase elevations > 3x ULN)", "Pregnancy and breastfeeding (statins strictly contraindicated)"],
            is_dose_model_ready=True,
            treatment_protocols=CLINICAL_PROTOCOLS.get("dyslipidemia", [])
        ),

        "hypothyroidism": DiseaseCoverageEntry(
            disease_id="hypothyroidism",
            disease_name="Hypothyroidism (Primary & Subclinical)",
            category="Endocrinology",
            icd_10_codes=["E03.9", "E02", "E06.3"],
            evidence_coverage="Active (Endocrine Society of India Clinical Practice Guidelines on Management of Hypothyroidism, 2022; ATA Guidelines for Thyroid Hormone Replacement).",
            evidence_sources=["ESI_THYROID_2022", "ATA_HYPOTHYROID_2021"],
            medicine_selection_coverage="Synthetic levothyroxine: Levothyroxine Sodium (T4 monotherapy). T3/combination therapies are not routinely recommended.",
            candidate_medicines=["Levothyroxine Sodium PO"],
            dose_method_coverage="Full replacement: ~1.6 mcg/kg/day (typically 50-100 mcg PO OD). Elderly or known coronary artery disease: Start low at 25-50 mcg PO OD, titrating by 12.5-25 mcg every 6-8 weeks.",
            dose_method_type="GUIDELINE_ALGORITHM",
            model_evaluation_status="Endocrine Society of India Guideline Algorithm with Weight & Age Titration.",
            supported_age_group="All ages (including neonates, children, adults, elderly)",
            supported_subtypes=["Overt Primary Hypothyroidism", "Subclinical Hypothyroidism (TSH > 10 or symptomatic)", "Hashimoto's Autoimmune Thyroiditis", "Post-Thyroidectomy / Radioiodine"],
            supported_severity=["Mild / Subclinical", "Moderate", "Severe / Myxedema"],
            supported_care_setting=["Outpatient Endocrinology / Primary Care"],
            required_inputs=["age", "weight_kg"],
            missing_data_requirements=["Serum TSH (mIU/L)", "Free T4 (ng/dL)", "Known coronary artery disease or cardiac arrhythmias", "Pregnancy status (requires immediate 25-30% dose increase)"],
            subtype_prompt_guidance="Specify baseline serum TSH and whether patient has pre-existing ischemic heart disease requiring lower starting dose.",
            exclusions=["Untreated subclinical or overt adrenal insufficiency (levothyroxine may precipitate acute adrenal crisis; replace hydrocortisone first)", "Acute myocardial infarction (delay full titration)"],
            is_dose_model_ready=True,
            treatment_protocols=CLINICAL_PROTOCOLS.get("hypothyroidism", [])
        ),

        "acute_gastroenteritis": DiseaseCoverageEntry(
            disease_id="acute_gastroenteritis",
            disease_name="Acute Gastroenteritis & Diarrheal Dehydration",
            category="Gastrointestinal / Infectious",
            icd_10_codes=["A09", "K52.9"],
            evidence_coverage="Active (ICMR Standard Treatment Workflow for Acute Diarrheal Disease in Adults and Children, 2022; WHO Guidelines for the Clinical Management of Acute Diarrhea).",
            evidence_sources=["ICMR_DIARRHEA_2022", "WHO_DIARRHEA_2021"],
            medicine_selection_coverage="Supportive rehydration: Oral Rehydration Salts (WHO low-osmolarity formula); Zinc supplementation (for children & adults); Antisecretory: Racecadotril; Antibiotics restricted to invasive bacterial dysentery (Ofloxacin + Ornidazole).",
            candidate_medicines=["Oral Rehydration Salts (ORS)", "Zinc Sulfate PO", "Racecadotril PO", "Ofloxacin + Ornidazole PO"],
            dose_method_coverage="ORS: 1 sachet in 1 liter clean water, sip freely (200-400 ml after each loose stool). Zinc: 20 mg PO OD x 14 days. Racecadotril 100 mg PO TID. Antimicrobials withheld unless bloody/mucoid dysentery.",
            dose_method_type="GUIDELINE_ALGORITHM",
            model_evaluation_status="WHO / ICMR Dehydration Protocol with Antimicrobial Stewardship Gating.",
            supported_age_group="Pediatrics, Adolescents, Adults, Elderly",
            supported_subtypes=["Acute Watery Diarrhea", "Invasive Bacterial Dysentery", "Traveler's Diarrhea", "Viral Gastroenteritis (Rotavirus/Norovirus)"],
            supported_severity=["No Dehydration", "Some Dehydration", "Severe Dehydration / Hypovolemic Shock"],
            supported_care_setting=["Primary Health Centre / Emergency Room / Outpatient Clinic"],
            required_inputs=["age", "weight_kg"],
            missing_data_requirements=["Clinical dehydration assessment (skin turgor, sunken eyes, thirst, mucous membranes)", "Presence of blood or mucus in stool", "Duration of loose stools", "Urine output in last 6-8 hours"],
            subtype_prompt_guidance="Differentiate acute non-invasive watery diarrhea (rehydration + racecadotril + zinc; no antibiotics) from invasive dysentery (bloody stools, high fever; requires targeted antimicrobial).",
            exclusions=["Loperamide and anti-motility agents are STRICTLY CONTRAINDICATED in children and in invasive/bloody diarrhea (risk of toxic megacolon and prolonged mucosal invasion)", "Severe hypovolemic shock (requires immediate emergency IV Ringer Lactate fluid resuscitation, not oral ORS alone)"],
            is_dose_model_ready=True,
            treatment_protocols=CLINICAL_PROTOCOLS.get("acute_gastroenteritis", [])
        ),

        "migraine": DiseaseCoverageEntry(
            disease_id="migraine",
            disease_name="Migraine & Tension-Type Headache",
            category="Neurology",
            icd_10_codes=["G43.9", "G43.0", "G44.2"],
            evidence_coverage="Active (ICMR Standard Treatment Workflow for Headaches and Migraine, 2022; International Headache Society / AHS Guidelines for Acute and Preventive Migraine Treatment).",
            evidence_sources=["ICMR_HEADACHE_2022", "AHS_MIGRAINE_2022"],
            medicine_selection_coverage="Acute abortive therapy: Naproxen + Domperidone (first line NSAID + antiemetic); Sumatriptan (5HT 1B/1D agonist for severe attacks); Paracetamol. Prophylaxis: Propranolol; Amitriptyline; Topiramate; Flunarizine.",
            candidate_medicines=["Naproxen + Domperidone PO", "Sumatriptan Succinate PO", "Paracetamol PO", "Propranolol Hydrochloride PO", "Flunarizine PO"],
            dose_method_coverage="Acute: Naproxen 500mg + Domperidone 10mg stat at onset. Sumatriptan 50 mg PO stat at onset (max 100-200 mg/day). Prophylaxis: Propranolol 40 mg PO OD or Flunarizine 5-10 mg PO at bedtime.",
            dose_method_type="GUIDELINE_ALGORITHM",
            model_evaluation_status="ICMR 2022 / AHS Clinical Practice Guideline Algorithm.",
            supported_age_group="Adolescents and Adults (>= 12 yrs)",
            supported_subtypes=["Migraine without Aura", "Migraine with Aura", "Chronic Migraine (>15 headache days/month)", "Frequent Episodic Tension-Type Headache"],
            supported_severity=["Mild", "Moderate", "Severe / Disabling"],
            supported_care_setting=["Outpatient Neurology / Primary Health Care"],
            required_inputs=["age", "weight_kg"],
            missing_data_requirements=["Frequency of headache days per month (to assess need for prophylaxis)", "Associated symptoms (photophobia, phonophobia, nausea, visual aura)", "Blood pressure (rule out hypertensive crisis)", "Cardiovascular risk profile (mandatory before triptan prescription)"],
            subtype_prompt_guidance="Evaluate whether patient requires acute abortive therapy alone or co-initiation of daily prophylactic therapy (indicated if >= 3-4 disabling attacks per month).",
            exclusions=["Sumatriptan is STRICTLY CONTRAINDICATED in patients with known ischemic heart disease, previous myocardial infarction, uncontrolled hypertension, peripheral vascular disease, or history of stroke/TIA", "Propranolol is contraindicated in patients with active Bronchial Asthma, severe COPD, or high-degree AV block"],
            is_dose_model_ready=True,
            treatment_protocols=CLINICAL_PROTOCOLS.get("migraine", [])
        ),

        "allergic_rhinitis_urticaria": DiseaseCoverageEntry(
            disease_id="allergic_rhinitis_urticaria",
            disease_name="Allergic Rhinitis & Chronic Urticaria",
            category="Immunology / Dermatology / Respiratory",
            icd_10_codes=["J30.9", "L50.0", "L50.8"],
            evidence_coverage="Active (ICMR Standard Treatment Workflow for Allergic Rhinitis, 2022; EAACI/GA2LEN/EDF/WAO Guideline for the Definition, Classification, Diagnosis and Management of Urticaria).",
            evidence_sources=["ICMR_ALLERGY_2022", "EAACI_URTICARIA_2022"],
            medicine_selection_coverage="Non-sedating second-generation H1 antihistamines: Bilastine (first-line); Levocetirizine; Fexofenadine. Dual controller: Levocetirizine + Montelukast. Intranasal corticosteroids: Fluticasone Furoate Nasal Spray.",
            candidate_medicines=["Bilastine 20mg PO", "Levocetirizine + Montelukast PO", "Fluticasone Furoate Nasal Spray", "Fexofenadine Hydrochloride PO"],
            dose_method_coverage="Bilastine 20 mg PO OD on empty stomach. Levocetirizine 5mg + Montelukast 10mg PO OD at bedtime. Fluticasone nasal spray 2 sprays each nostril OD.",
            dose_method_type="GUIDELINE_ALGORITHM",
            model_evaluation_status="ICMR 2022 / EAACI Clinical Practice Guideline Protocol.",
            supported_age_group="Children (>= 6 yrs), Adolescents, and Adults",
            supported_subtypes=["Seasonal Allergic Rhinitis (Hay Fever)", "Perennial Allergic Rhinitis", "Acute Urticaria", "Chronic Spontaneous Urticaria"],
            supported_severity=["Mild Intermittent", "Moderate Persistent", "Severe Persistent"],
            supported_care_setting=["Outpatient Allergy Clinic / Primary Care"],
            required_inputs=["age", "weight_kg"],
            missing_data_requirements=["Duration and frequency of symptoms", "Associated eye symptoms (allergic conjunctivitis) or bronchospasm (allergic asthma comorbidity)", "Known specific triggers / allergen exposure history", "Presence of angioedema (swelling of lips, tongue, or airway requiring emergency adrenaline)"],
            subtype_prompt_guidance="Screen for laryngeal angioedema or anaphylaxis (stridor, breathing difficulty, hypotension) which requires emergency intramuscular Adrenaline (Epinephrine 0.5mg IM stat), NOT oral antihistamines alone.",
            exclusions=["Anaphylaxis or acute angioedema with airway compromise is a critical medical emergency requiring immediate 1:1000 IM Adrenaline", "First-generation sedating antihistamines (Chlorpheniramine, Hydroxyzine) should be avoided during daytime driving or machinery operation"],
            is_dose_model_ready=True,
            treatment_protocols=CLINICAL_PROTOCOLS.get("allergic_rhinitis_urticaria", [])
        ),

        "copd": DiseaseCoverageEntry(
            disease_id="copd",
            disease_name="Chronic Obstructive Pulmonary Disease (COPD)",
            category="Respiratory",
            icd_10_codes=["J44.9", "J44.0", "J44.1"],
            evidence_coverage="Active (ICMR Standard Treatment Workflow for Chronic Obstructive Pulmonary Disease, 2022; GOLD 2024 Global Strategy for Prevention, Diagnosis and Management of COPD).",
            evidence_sources=["ICMR_COPD_2022", "GOLD_COPD_2024"],
            medicine_selection_coverage="Inhaled dual bronchodilators: Tiotropium + Formoterol (LAMA + LABA); Glycopyrronium + Formoterol. Mucolytic: N-Acetylcysteine. Exacerbation therapy: Prednisolone tablets; Amoxicillin-Clavulanate / Azithromycin for purulent sputum.",
            candidate_medicines=["Tiotropium + Formoterol Inhaler", "Salbutamol + Ipratropium Respules", "N-Acetylcysteine 600mg PO", "Prednisolone Tablets PO"],
            dose_method_coverage="Maintenance: Tiotropium 18mcg + Formoterol 12mcg 1 puff BD via inhaler with spacer. Mucolytic: N-Acetylcysteine 600 mg PO BD effervescent. Acute flare: Prednisolone 40 mg PO OD x 5 days.",
            dose_method_type="GUIDELINE_ALGORITHM",
            model_evaluation_status="GOLD 2024 / ICMR Clinical Practice Guideline Protocol.",
            supported_age_group="Adults (>= 40 yrs, typically with smoking or biomass fuel exposure history)",
            supported_subtypes=["GOLD Group A (Low symptoms, low exacerbation)", "GOLD Group B (High symptoms, low exacerbation)", "GOLD Group E (Exacerbation prone >= 2 flares/year)"],
            supported_severity=["Moderate (FEV1 50-79%)", "Severe (FEV1 30-49%)", "Very Severe (FEV1 < 30%)"],
            supported_care_setting=["Pulmonology Outpatient / Primary Health Centre / Inpatient Respiratory Ward"],
            required_inputs=["age", "weight_kg"],
            missing_data_requirements=["Post-bronchodilator Spirometry (FEV1/FVC < 0.70 confirms persistent airflow limitation)", "Current resting SpO2 on room air", "History of moderate/severe exacerbations in past 12 months", "Biomass smoke or tobacco smoking history (pack-years)"],
            subtype_prompt_guidance="Specify whether patient is in stable maintenance phase or presenting with Acute Exacerbation of COPD (AECOPD with worsening dyspnea, increased sputum volume, or purulence).",
            exclusions=["Do NOT prescribe non-selective beta-blockers (Propranolol, Carvedilol high dose) due to risk of fatal bronchoconstriction", "Avoid high-flow uncontrolled oxygen delivery (target SpO2 88-92% to prevent hypercapnic respiratory drive suppression)"],
            is_dose_model_ready=True,
            treatment_protocols=CLINICAL_PROTOCOLS.get("copd", [])
        )
    }

