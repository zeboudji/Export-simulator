rapport = {
    "Droits de Douane (%)": droits_douane_taux,
    "Droits de Douane (DZD)": droits_douane,
    "Droits de Douane (EUR)": droits_douane_eur,
    "TVA (%)": TVA_TAUX,
    "TVA (DZD)": TVA,
    "TVA (EUR)": TVA_eur,
    "TIC (%)": TIC_TAUX,
    "TIC (DZD)": TIC,
    "TIC (EUR)": TIC_eur,
    "Frais Annexes (DZD)": frais_annexes,
    "Frais Annexes (EUR)": frais_annexes_eur,
    "Total Estimé (DZD)": total_dzd,
    "Total Estimé (EUR)": total_eur,
    "Taux de Conversion (DZD/EUR)": conversion_rate,
    "Devise du Prix": price_currency
}

df = pd.DataFrame([rapport])
