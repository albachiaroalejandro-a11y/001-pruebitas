# ==========================================
# 🏷️ 2. TU UNIVERSO DE ETIQUETAS
# ==========================================
# PEGÁ ACÁ ADENTRO TU DICCIONARIO "universo" COMPLETO DE 100+ TICKERS
universo = {
    # ==========================================
    # 🛒 CONSUMO DEFENSIVO, BEBIDAS Y ALIMENTOS
    # ==========================================
    "KO": {"Bebidas", "ConsumoDefensivo", "Dividendos"},
    "PEP": {"Bebidas", "ConsumoDefensivo", "Dividendos", "Snacks"},
    "ABEV": {"Bebidas", "ConsumoDefensivo", "Brasil"},
    "DEO": {"Bebidas", "ConsumoDefensivo", "Europa"},
    "MDLZ": {"Snacks", "ConsumoDefensivo", "Alimentos"},
    "PG": {"CuidadoPersonal", "ConsumoDefensivo", "Dividendos"},
    "UL": {"CuidadoPersonal", "ConsumoDefensivo", "Dividendos"},
    "CL": {"CuidadoPersonal", "ConsumoDefensivo", "Dividendos"},
    "WMT": {"Retail", "ConsumoDefensivo", "Supermercados"},
    "COST": {"Retail", "ConsumoDefensivo", "Supermercados"},

    # ==========================================
    # 🛍️ CONSUMO DISCRECIONAL Y RETAIL
    # ==========================================
    "HD": {"Retail", "ConsumoDiscrecional", "Dividendos", "Construccion"},
    "LOW": {"Retail", "ConsumoDiscrecional", "Construccion"},
    "TGT": {"Retail", "ConsumoDiscrecional", "Supermercados"},
    "NKE": {"Indumentaria", "ConsumoDiscrecional", "Dividendos"},
    "MCD": {"FastFood", "ConsumoDiscrecional", "Dividendos"},
    "SBUX": {"FastFood", "ConsumoDiscrecional", "Dividendos"},
    "ARCO": {"FastFood", "ConsumoDiscrecional", "Latam", "Snacks"},

    # ==========================================
    # 💻 TECNOLOGÍA, MEGA-CAPS Y SOFTWARE
    # ==========================================
    "AAPL": {"Tech", "Hardware", "MegaCap"},
    "MSFT": {"Tech", "Software", "MegaCap", "IA"},
    "GOOGL": {"Tech", "Software", "MegaCap", "IA", "Publicidad"},
    "META": {"Tech", "Software", "MegaCap", "Publicidad", "IA"},
    "AMZN": {"Tech", "Ecommerce", "MegaCap", "Retail"},
    "ADBE": {"Tech", "Software"},
    "SNOW": {"Tech", "Software", "IA"},
    "PLTR": {"Tech", "Software", "IA"},
    "IBM": {"Tech", "Software", "Dividendos", "IA", "InfraestructuraIT"},
    "CSCO": {"Tech", "Hardware", "Redes"},
    "NOK": {"Tech", "Hardware", "Redes"},
    "MSI": {"Tech", "Hardware", "Comunicaciones"},
    "HPQ": {"Tech", "Hardware"},
    "SONY": {"Tech", "Hardware", "Entretenimiento"},
    "KEEL": {"MineriaDigital", "Datacenters", "InfraestructuraIT", "HPC", "Blockchain", "Tech"}, # Ex Bitfarms

    # ==========================================
    # 📦 E-COMMERCE (INTERNACIONAL Y EMERGENTE)
    # ==========================================
    "MELI": {"Ecommerce", "Tech", "Latam"},
    "BABA": {"Ecommerce", "Tech", "China"},
    "JD": {"Ecommerce", "Tech", "China"},
    "SHOP": {"Ecommerce", "Tech", "Software"},
    "EBAY": {"Ecommerce", "Tech"},
    "SE": {"Ecommerce", "Tech", "Emergentes"},
    "JMIA": {"Ecommerce", "Tech", "Emergentes"},

    # ==========================================
    # 📱 STREAMING Y ENTRETENIMIENTO
    # ==========================================
    "DIS": {"Entretenimiento", "Streaming", "ConsumoDiscrecional"},
    "NFLX": {"Entretenimiento", "Streaming", "Tech"},
    "SPOT": {"Entretenimiento", "Streaming", "Tech"},

    # ==========================================
    # 🧠 SEMICONDUCTORES (EL CICLO DEL SILICIO)
    # ==========================================
    "NVDA": {"Semiconductores", "Tech", "MegaCap", "IA"},
    "AMD": {"Semiconductores", "Tech", "IA"},
    "INTC": {"Semiconductores", "Tech"},
    "TSM": {"Semiconductores", "Tech", "Hardware"},
    "AVGO": {"Semiconductores", "Tech", "Dividendos"},
    "QCOM": {"Semiconductores", "Tech"},
    "MU": {"Semiconductores", "Tech"},
    "TXN": {"Semiconductores", "Tech", "Dividendos"},

    # ==========================================
    # 💳 FINANCIERAS, BANCOS Y FINTECH
    # ==========================================
    "JPM": {"Financiera", "Bancos", "Dividendos"},
    "C": {"Financiera", "Bancos", "Dividendos"},
    "WFC": {"Financiera", "Bancos", "Dividendos"},
    "GS": {"Financiera", "Bancos", "Inversion"},
    "V": {"Financiera", "Pagos", "Tech"},
    "MA": {"Financiera", "Pagos", "Tech"},
    "AXP": {"Financiera", "Pagos", "Dividendos"},
    "PYPL": {"Financiera", "Pagos", "Fintech"},
    "UPST": {"Financiera", "Fintech", "IA"},
    "BRK-B": {"Financiera", "Conglomerado"},

    # ==========================================
    # 🌎 LATAM Y BRASIL (FINANZAS Y ENERGÍA)
    # ==========================================
    "BBD": {"Financiera", "Bancos", "Brasil"},
    "ITUB": {"Financiera", "Bancos", "Brasil"},
    "NU": {"Financiera", "Fintech", "Brasil", "Latam"},
    "PAGS": {"Financiera", "Pagos", "Fintech", "Brasil"},
    "STNE": {"Financiera", "Pagos", "Fintech", "Brasil"},
    "PBR": {"Energia", "Petroleo", "Brasil"},
    "GPRK": {"Energia", "Petroleo", "Latam"},
    "VIST": {"Energia", "Petroleo", "Argentina", "Latam"},
    "AGRO": {"Agro", "Alimentos", "Latam"},

    # ==========================================
    # 💉 SALUD Y FARMACÉUTICAS
    # ==========================================
    "JNJ": {"Farma", "Salud", "Dividendos"},
    "PFE": {"Farma", "Salud", "Dividendos"},
    "LLY": {"Farma", "Salud", "Dividendos"},
    "BMY": {"Farma", "Salud", "Dividendos"},
    "GILD": {"Farma", "Salud", "Dividendos"},
    "MRNA": {"Farma", "Salud", "Biotecnologia"},
    "UNH": {"Salud", "Seguros", "Dividendos"},
    "ABT": {"Salud", "Farma", "Dividendos"},

    # ==========================================
    # 🛢️ ENERGÍA Y PETRÓLEO
    # ==========================================
    "XOM": {"Energia", "Petroleo", "Dividendos"},
    "CVX": {"Energia", "Petroleo", "Dividendos"},
    "OXY": {"Energia", "Petroleo", "Dividendos"},
    "SHEL": {"Energia", "Petroleo", "Europa", "Dividendos"},

    # ==========================================
    # 🚜 INDUSTRIA, AUTOMOTRIZ Y AEROESPACIAL
    # ==========================================
    "CAT": {"Industrial", "Maquinaria", "Dividendos"},
    "DE": {"Industrial", "Maquinaria", "Agro"},
    "GE": {"Industrial", "Conglomerado"},
    "MMM": {"Industrial", "Conglomerado", "Dividendos"},
    "F": {"Automotriz", "Industrial", "Dividendos"},
    "GM": {"Automotriz", "Industrial"},
    "TM": {"Automotriz", "Industrial", "Asia"},
    "STLA": {"Automotriz", "Industrial", "Europa"},
    "TSLA": {"Automotriz", "VehiculosElectricos", "Tech", "ConsumoDiscrecional"},
    "NIO": {"Automotriz", "VehiculosElectricos", "China", "ConsumoDiscrecional"},
    "RACE": {"Automotriz", "Lujo", "ConsumoDiscrecional"},
    "BA": {"Aeroespacial", "Industrial", "Defensa"},
    "RTX": {"Aeroespacial", "Industrial", "Defensa"},
    "SPCE": {"Aeroespacial", "Turismo"},
    "SATL": {"Aeroespacial", "Tech", "Latam"},
    "AAL": {"Aeroespacial", "Transporte", "ConsumoDiscrecional", "Turismo", "Industrial"}, # American Airlines Group

    # ==========================================
    # ⛏️ MINERÍA Y MATERIALES
    # ==========================================
    "VALE": {"Mineria", "Hierro", "Brasil"},
    "RIO": {"Mineria", "Hierro", "Dividendos"},
    "TX": {"Materiales", "Acero", "Latam"},
    "DOW": {"Materiales", "Quimica", "Dividendos"},
    "HMY": {"Mineria", "Oro"},
    "GOLD": {"Mineria", "Oro"},
    "NEM": {"Mineria", "Oro"},
    "PAAS": {"Mineria", "Plata"},
    "LAC": {"Mineria", "Litio", "Materiales"},
    "BG": {"Agro", "Dividendos"},

    # ==========================================
    # 📞 TELECOMUNICACIONES
    # ==========================================
    "T": {"Telecomunicaciones", "Dividendos"},
    "VZ": {"Telecomunicaciones", "Dividendos"},

    # ==========================================
    # 📊 ETFs E ÍNDICES (CRUZAN SOLO ENTRE ELLOS)
    # ==========================================
    "SPY": {"ETF", "MercadoUS"},
    "DIA": {"ETF", "MercadoUS"},
    "QQQ": {"ETF", "MercadoUS", "Tech"},
    "IWM": {"ETF", "MercadoUS", "SmallCaps"},
    "EEM": {"ETF", "Emergentes"},
    "EWZ": {"ETF", "Brasil"},
    "ARKK": {"ETF", "Tech", "Innovacion"},
    "GLD": {"ETF", "Oro"},
    "COPX": {"ETF", "Cobre", "Mineria"},
    "XLE": {"ETF", "Energia"},
    "XLF": {"ETF", "Financiera"},
    "XME": {"ETF", "Mineria"},
    
    # ⚠️ PELIGRO: DERIVADOS Y APALANCADOS
    "TQQQ": {"ETF", "Derivados", "Tech"},
    "SH": {"ETF", "Derivados", "MercadoUS"},
    "VXX": {"ETF", "Derivados", "Volatilidad"}
}
# Al final de todo en universo.py
tickers = list(universo.keys())