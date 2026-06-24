from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from datetime import datetime

app = Flask(__name__)

# Intent Excel

try:
    # data = pd.read_excel("Intent_Chatbot_Informasi_LPPAPSI_COMPLETE.xlsx")
    data = pd.read_excel("Intent_Chatbot.xlsx")
    patterns = data["pattern"].astype(str).tolist()
    responses = data["response"].tolist()
    
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(patterns)
    print("✅ Data loaded successfully!")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    patterns = []
    responses = []

# =====================
# MENU STRUCTURE - IMPROVED WITH 3 CATEGORIES
# =====================
MENU_BUTTONS = {
    "main": [
        {"text": "📚 Pelatihan & Sertifikasi", "callback": "all_programs"},
        {"text": "📅 Jadwal Pelatihan", "callback": "jadwal_menu"},
        {"text": "💰 Biaya Pelatihan", "callback": "biaya_menu"},
        {"text": "📝 Cara Daftar", "callback": "cara_daftar"},
        {"text": "📞 Kontak Kami", "callback": "kontak"},
    ],

    # KATEGORI PERUSAHAAN JADWAL
    "kategori_perusahaan_jadwal": [
        {"text": "📊 Pelatihan Basic Accounting", "callback": "jadwal_basic_accounting"},
        {"text": "🛡️ Pelatihan Memahami Dasar-Dasar Manajemen Risiko", "callback": "jadwal_manajemen_risiko"},
        {"text": "🔍 Pelatihan Audit Internal", "callback": "jadwal_audit"},
        {"text": "🔍 Pelatihan  Basic Financial Modelling", "callback": "jadwal_financial"},
        {"text": "💼 Brevet A&B Terpadu", "callback": "jadwal_brevet"},
        {"text": "📈 Strategy, Performance, and Control Course", "callback": "jadwal_spc"},
        {"text": "📊 Pelatihan Enterprise Risk Management(ERM)", "callback": "jadwal_erm"},
        {"text": "🔍 Governance, Control, and Risk Management", "callback": "jadwal_gcrm"},
        {"text": "🔍 Budgeting and Cost Control Training", "callback": "jadwal_bcc"},
        {"text": "🔍 Financial Analysis and Corporate Valuation", "callback": "jadwal_facv"},
        {"text": "🔍 Pelatihan Advance Excel", "callback": "jadwal_excel"},
        {"text": "🔍 Pelatihan PSAK Komprehensif", "callback": "jadwal_psak"},
        {"text": "🔙 Menu Utama", "callback": "main_menu"},
    ],

    # KATEGORI SERTIFIKASI
    "kategori_sertifikasi_jadwal": [
        {"text": "📚 CPSAK Review", "callback": "jadwal_cpsak"},
        {"text": "📖 USAS Review", "callback": "jadwal_usas"},
        {"text": "🛡️ CRMO Review", "callback": "jadwal_crmo"},
        {"text": "🌐 CSRS Review", "callback": "jadwal_csrs"},
        {"text": "💻 Data Analyst", "callback": "jadwal_analyst"},
        {"text": "🌐 CPMA Review", "callback": "jadwal_cpma"},
        {"text": "🌐 USKP Review", "callback": "jadwal_uskp"},
        {"text": "🎓 CA Review", "callback": "jadwal_ca"},
        {"text": "🌟 CPA Review", "callback": "jadwal_cpa"},
        {"text": "🔙 Menu Utama", "callback": "main_menu"},
    ],

    # KATEGORI PEMERINTAH
    "kategori_pemerintah_jadwal": [
        {"text": "💰 Bimtek Penyusunan Laporan Keuangan Pemerintah Daerah", "callback": "jadwal_lapkeuangan"},
        {"text": "🏛️ Bimtek Keuangan Daerah Terpadu", "callback": "jadwal_keudaerah"},
        {"text": "📦 Bimtek Pengelolaan Barang Milik Negara/Daerah", "callback": "jadwal_pbmn"},
        {"text": "🏢 Bimtek Pajak dan Retribusi Daerah", "callback": "jadwal_retribusi"},
        {"text": "📋 CGAA Review", "callback": "jadwal_cgaa"},
        {"text": "📋 CGAE Review", "callback": "jadwal_cgae"},
        {"text": "📋 Pelatihan Pembukuan, Inventarisasi, dan Pelaporan Barang Milik Daerah", "callback": "jadwal_pembukuan"},
        {"text": "📊 BLUD Puskesmas", "callback": "jadwal_blud"},
        {"text": "🔙 Menu Utama", "callback": "main_menu"},
    ],
    
    # KATEGORI PERUSAHAAN Biaya
    "kategori_perusahaan": [
        {"text": "📊 Pelatihan Basic Accounting", "callback": "biaya_basic_accounting"},
        {"text": "🛡️ Pelatihan Memahami Dasar-Dasar Manajemen Risiko", "callback": "biaya_manajemen_risiko"},
        {"text": "🔍 Pelatihan Audit Internal", "callback": "biaya_audit"},
        {"text": "🔍 Pelatihan  Basic Financial Modelling", "callback": "biaya_financial"},
        {"text": "💼 Brevet A&B Terpadu", "callback": "biaya_brevet"},
        {"text": "📈 Strategy, Performance, and Control Course", "callback": "biaya_spc"},
        {"text": "📊 Pelatihan Enterprise Risk Management(ERM)", "callback": "biaya_erm"},
        {"text": "🔍 Governance, Control, and Risk Management", "callback": "biaya_gcrm"},
        {"text": "🔍 Budgeting and Cost Control Training", "callback": "biaya_bcc"},
        {"text": "🔍 Financial Analysis and Corporate Valuation", "callback": "biaya_facv"},
        {"text": "🔍 Pelatihan Advance Excel", "callback": "biaya_excel"},
        {"text": "🔍 Pelatihan PSAK Komprehensif", "callback": "biaya_psak"},
        {"text": "🔙 Menu Utama", "callback": "main_menu"},
    ],
    
    # KATEGORI SERTIFIKASI
    "kategori_sertifikasi": [
        {"text": "📚 CPSAK Review", "callback": "biaya_cpsak"},
        {"text": "📖 USAS Review", "callback": "biaya_usas"},
        {"text": "🛡️ CRMO Review", "callback": "biaya_crmo"},
        {"text": "🌐 CSRS Review", "callback": "biaya_csrs"},
        {"text": "💻 Data Analyst", "callback": "biaya_analyst"},
        {"text": "🌐 CPMA Review", "callback": "biaya_cpma"},
        {"text": "🌐 USKP Review", "callback": "biaya_uskp"},
        {"text": "🎓 CA Review", "callback": "biaya_ca"},
        {"text": "🌟 CPA Review", "callback": "biaya_cpa"},
        {"text": "🔙 Menu Utama", "callback": "main_menu"},
    ],
    
    # KATEGORI PEMERINTAH
    "kategori_pemerintah": [
        {"text": "💰 Bimtek Penyusunan Laporan Keuangan Pemerintah Daerah", "callback": "biaya_lapkeuangan"},
        {"text": "🏛️ Bimtek Keuangan Daerah Terpadu", "callback": "biaya_keudaerah"},
        {"text": "📦 Bimtek Pengelolaan Barang Milik Negara/Daerah", "callback": "biaya_pbmn"},
        {"text": "🏢 Bimtek Pajak dan Retribusi Daerah", "callback": "biaya_retribusi"},
        {"text": "📋 CGAA Review", "callback": "biaya_cgaa"},
        {"text": "📋 CGAE Review", "callback": "biaya_cgae"},
        {"text": "📋 Pelatihan Pembukuan, Inventarisasi, dan Pelaporan Barang Milik Daerah", "callback": "biaya_pembukuan"},
        {"text": "📊 BLUD Puskesmas", "callback": "biaya_blud"},
        {"text": "🔙 Menu Utama", "callback": "main_menu"},
    ],
    
    # INFO & KONTAK
    "info_kontak": [
        {"text": "📞 Kontak Kami", "callback": "kontak"},
        {"text": "📝 Cara Daftar", "callback": "cara_daftar"},
        {"text": "🔙 Menu Utama", "callback": "main_menu"},
    ]
}

# =====================
# QUICK SEARCH DATABASE - For direct answers
# =====================
QUICK_SEARCH_DB = {
    # Keywords : {program_name, biaya_callback, jadwal_callback}
    "basic accounting": {"biaya": "biaya_basic_accounting", "jadwal": "jadwal_basic_accounting"},
    "akuntansi dasar": {"biaya": "biaya_basic_accounting", "jadwal": "jadwal_basic_accounting"},
    "manajemen risiko": {"biaya": "biaya_manajemen_risiko", "jadwal": "jadwal_manajemen_risiko"},
    "audit internal": {"biaya": "biaya_audit", "jadwal": "jadwal_audit"},
    "audit": {"biaya": "biaya_audit", "jadwal": "jadwal_audit"},
    "brevet": {"biaya": "biaya_brevet", "jadwal": "jadwal_brevet"},
    "transfer pricing": {"biaya": "biaya_financial", "jadwal": "jadwal_financial"},
    "financial": {"biaya": "biaya_financial", "jadwal": "jadwal_financial"},
    "enterprise risk": {"biaya": "biaya_erm", "jadwal": "jadwal_erm"},
    "erm": {"biaya": "biaya_erm", "jadwal": "jadwal_erm"},
    "cpsak": {"biaya": "biaya_cpsak", "jadwal": "jadwal_cpsak"},
    "usas": {"biaya": "biaya_usas", "jadwal": "jadwal_usas"},
    "crmo": {"biaya": "biaya_crmo", "jadwal": "jadwal_crmo"},
    "csrs": {"biaya": "biaya_csrs", "jadwal": "jadwal_csrs"},
    "data analyst": {"biaya": "biaya_analyst", "jadwal": "jadwal_analyst"},
    "analyst": {"biaya": "biaya_analyst", "jadwal": "jadwal_analyst"},
    "ca review": {"biaya": "biaya_ca", "jadwal": "jadwal_ca"},
    "cpa review": {"biaya": "biaya_cpa", "jadwal": "jadwal_cpa"},
    "uskp": {"biaya": "biaya_uskp", "jadwal": "jadwal_uskp"},
    "laporan keuangan": {"biaya": "biaya_lapkeuangan", "jadwal": "jadwal_lapkeuangan"},
    "keuangan daerah": {"biaya": "biaya_keudaerah", "jadwal": "jadwal_keudaerah"},
    "bmn": {"biaya": "biaya_pbmn", "jadwal": "jadwal_pbmn"},
    "barang milik negara": {"biaya": "biaya_pbmn", "jadwal": "jadwal_pbmn"},
    "pajak daerah": {"biaya": "biaya_retribusi", "jadwal": "jadwal_retribusi"},
    "retribusi": {"biaya": "biaya_retribusi", "jadwal": "jadwal_retribusi"},
    "cgaa": {"biaya": "biaya_cgaa", "jadwal": "jadwal_cgaa"},
    "cgae": {"biaya": "biaya_cgae", "jadwal": "jadwal_cgae"},
    "blud": {"biaya": "biaya_blud", "jadwal": "jadwal_blud"},
    "puskesmas": {"biaya": "biaya_blud", "jadwal": "jadwal_blud"},
}

# =====================
# NAMED ENTITY RECOGNITION - IMPROVED
# =====================
def extract_entities(text):
    """Extract entities from user input"""
    entities = {
        "money": [],
        "program_name": None,
        "intent": None
    }
    
    text_lower = text.lower()
    
    # Extract money amounts
    money_pattern = r'rp\.?\s*[\d.,]+'
    money_matches = re.findall(money_pattern, text_lower)
    entities["money"] = money_matches
    
    # QUICK SEARCH - Match program name
    for keyword, callbacks in QUICK_SEARCH_DB.items():
        if keyword in text_lower:
            entities["program_name"] = keyword
            break
    
    # Detect intent
    if any(word in text_lower for word in ["jadwal", "kapan", "tanggal", "waktu", "schedule", 'jam']):
        entities["intent"] = "jadwal"
    elif any(word in text_lower for word in ["biaya", "harga", "tarif", "berapa", "bayar", "price", "cost"]):
        entities["intent"] = "biaya"
    elif any(word in text_lower for word in ["daftar", "registrasi", "pendaftaran", "register", 'cara', 'caranya']):
        entities["intent"] = "daftar"
    elif any(word in text_lower for word in ["kontak", "hubungi", "telepon", "email", 'nomor', 'admin', 'contact']):
        entities["intent"] = "kontak"
    elif any(word in text_lower for word in ["pelatihan apa", "ada apa", "program apa", "list", "daftar program"]):
        entities["intent"] = "list_programs"
    
    return entities

# =====================
# RESPONSE GENERATOR - WITH QUICK SEARCH
# =====================
def get_response(user_input):
    """Generate response using Quick Search or TF-IDF"""
    
    # Extract entities first
    entities = extract_entities(user_input)
    
    # ✅ QUICK SEARCH - Direct answer if program found
    if entities["program_name"] and entities["intent"] in ["biaya", "jadwal"]:
        program_key = entities["program_name"]
        intent = entities["intent"]
        
        # Get callback from quick search database
        callback_id = QUICK_SEARCH_DB[program_key].get(intent)
        if callback_id:
            # Get direct response
            response = handle_menu_callback(callback_id)
            return f"🔍 **Quick Search Result:**\n\n{response}"
    
    # Special intent handling
    if entities["intent"] == "list_programs":
        return generate_program_list()
    elif entities["intent"] == "kontak":
        return handle_menu_callback("kontak")
    elif entities["intent"] == "daftar":
        return handle_menu_callback("cara_daftar")
    
    # Use TF-IDF for general queries
    if patterns:
        user_vec = vectorizer.transform([user_input])
        similarity = cosine_similarity(user_vec, X)
        best_idx = similarity.argmax()
        score = similarity[0][best_idx]

        if score < 0.2:
            return generate_fallback_response(entities)
        
        return responses[best_idx]
    
    return "Maaf, coba beri pernyataan yang lebih spesifik atau pilih menu yang anda inginkan."

def generate_program_list():
    """Generate list of all available programs"""
    response = "📚 **Program Pelatihan LPPAPSI:**\n\n"
    response += "🏢 PELATIHAN PERUSAHAAN:\n"
    response += "• Basic Accounting\n• Dasar-Dasar Manajemen Risiko\n• Audit Internal\n• Brevet A&B Terpadu\n• Basic Financial Modeling\n• Strategy, Performance, and Control\n• Governance, Control, and Risk Management\n• Advanced Excel\n• Financial Analysis and Corporate Valuation\n• PSAK Komprehensif\n• Budgeting and Cost Control\n• Enterprise Risk Management(ERM)\n\n"
    response += "🎓 PELATIHAN SERTIFIKASI PROFESIONAL:\n"
    response += "• CPSAK Review\n• USAS Review\n• CRMO Review\n• CSRS Review\n• CPMA Review\n• Data Analyst\n• CA Review\n• CPA Review\n• USKP Review\n\n"
    response += "🏛️ PELATIHAN PEMERINTAH:\n"
    response += "• Penyusanan Laporan Keuangan Pemda\n• Keuangan Daerah Terpadu\n• Pengelolaan BMND Sesuai PP No. 28 Tahun 2020\n• Pajak & Retribusi Daerah Sesuai PP No. 10 Tahun 2021\n• CGAA/CGAE Review\n• Penyusunan Laporan Keuangan BLUD Puskesmas\n• Pembukuan, Inventarisasi, dan Pelaporan Barang Milik Daerah\n\n"
    response += "💡 **Cara cepat:** Ketik 'biaya [nama program]' atau 'jadwal [nama program]'\n"
    response += "Contoh: 'biaya brevet' atau 'jadwal cpsak'"
    return response

def generate_fallback_response(entities):
    """Generate smart fallback based on extracted entities"""
    if entities["intent"]:
        intent_responses = {
            "biaya": "💰 Untuk info biaya, silakan:\n1. Pilih kategori dari menu, ATAU\n2. Ketik: 'biaya [nama program]'\n\nContoh: 'biaya brevet' atau 'biaya cpsak'",
            "jadwal": "📅 Untuk info jadwal, silakan:\n1. Pilih kategori dari menu, ATAU\n2. Ketik: 'jadwal [nama program]'\n\nContoh: 'jadwal audit' atau 'jadwal ca review'",
        }
        return intent_responses.get(entities["intent"], "Maaf, saya belum memahami. Silakan pilih dari menu atau ketik lebih spesifik.")
    
    return "Halo! 👋 Saya ChatBot LPPAPSI.\n\nSilakan:\n✅ Pilih kategori dari menu, ATAU\n✅ Ketik langsung, contoh:\n   • 'biaya brevet'\n   • 'jadwal cpsak'\n   • 'kontak'"

# =====================
# MENU HANDLER - UNCHANGED (Your original code)
# =====================
def handle_menu_callback(callback):
    """menu button clicks"""
    responses_map = {
        "jadwal_pbjp": "📅 Jadwal Ujian PBJP\n\nUjian terdekat akan diadakan pada:\n- 16 Mei 2026\n- 20 Juni 2026\n- 17 Juli 2026\n\nSilahkan memilih tanggal yang sesuai, pendaftaran dapat dilakukan dengan menghubungi hotline kami.",
        "jadwal_brevet": "📅 Jadwal Brevet\n\nUjian terdekat akan diadakan pada:\n- 22 Mei 2026\n- 26 Juni 2026\n- 20 Juli 2026\n\nSilahkan memilih tanggal yang sesuai, pendaftaran dapat dilakukan dengan menghubungi hotline kami.",
        "jadwal_usas": "📅 Jadwal USAS Review\n\nUjian terdekat akan diadakan pada:\n- 17 Juni 2026\n\nPendaftaran dan pemilihan tanggal dapat dilakukan dengan menghubungi hotline kami",
        "jadwal_cpsak" : '📅 Jadwal CPSAK Review\n\nSaat ini jadwal pelatihan belum tersedia 😊\n Namun, Anda masih dapat melakukan pendaftaran dan berdiskusi terkait penentuan jadwal dengan menghubungi hotline kami. Silahkan ketik "Kontak" atau pilih menu "Kontak Kami".',
        'jadwal_crmo' : '📅 Jadwal CRMO Review\n\nSaat ini jadwal pelatihan belum tersedia 😊\n Namun, Anda masih dapat melakukan pendaftaran dan berdiskusi terkait penentuan jadwal dengan menghubungi hotline kami. Silahkan ketik "Kontak" atau pilih menu "Kontak Kami".',
        'jadwal_csrs' : '📅 Jadwal CSRS Review\n\nSaat ini jadwal pelatihan belum tersedia 😊\n Namun, Anda masih dapat melakukan pendaftaran dan berdiskusi terkait penentuan jadwal dengan menghubungi hotline kami. Silahkan ketik "Kontak" atau pilih menu "Kontak Kami".',
        'jadwal_cpma' : '📅 Jadwal CPMA Review\n\nSaat ini jadwal pelatihan belum tersedia 😊\n Namun, Anda masih dapat melakukan pendaftaran dan berdiskusi terkait penentuan jadwal dengan menghubungi hotline kami. Silahkan ketik "Kontak" atau pilih menu "Kontak Kami".',
        'jadwal_analyst' : '📅 Jadwal Pelatihan Data Analyst\n\nSaat ini jadwal pelatihan belum tersedia 😊\n Namun, Anda masih dapat melakukan pendaftaran dan berdiskusi terkait penentuan jadwal dengan menghubungi hotline kami. Silahkan ketik "Kontak" atau pilih menu "Kontak Kami".',
        'jadwal_ca' : '📅 Jadwal CA Review\n\nUjian terdekat akan diadakan pada:\n- 13 Juli 2026\n- 5 Oktober 2026\n Setiap Senin-Jumat, Pukul 15.00 - 17.00 WIB\n\nInfo lebih lanjut hubungi hotline kami.',
        'jadwal_cpa' : '📅 Jadwal CPA Review\n\nSaat ini jadwal pelatihan belum tersedia 😊\n Namun, Anda masih dapat melakukan pendaftaran dan berdiskusi terkait penentuan jadwal dengan menghubungi hotline kami. Silahkan ketik "Kontak" atau pilih menu "Kontak Kami".',
        'jadwal_uskp' : '📅 Jadwal USKP Review\n\nUjian terdekat akan diadakan pada:\n-3 Agustus 2026\nSetiap Senin-Jumat, pukul 15.00 - 17.00 WIB.\n\nPendaftaran dan pemilihan tanggal dapat dilakukan dengan menghubungi hotline kami',
        'jadwal_basic_accounting' : '📅 Jadwal Pelatihan Basic Accounting\n\nUjian terdekat akan diadakan pada:\n-8 Juni 2026\n Jadwal A Basic Accounting\n Senin, Rabu, dan Jumat, pukul 18.30 sd 21.00\n\n Jadwal B Basic Accounting Selasa, Kamis, dan Sabtu, pukul 18.30 sd 21.00\n\nPendaftaran dan pemilihan jadwal dapat dilakukan dengan menghubungi hotline kami',
        'jadwal_manajemen_risiko' : '📅 Jadwal Pelatihan Memahami Dasar-Dasar Manajemen Risiko\n\nUjian terdekat akan diadakan pada:\n- 27 Mei 2026\n Hari Rabu dan Kamis, pukul 09.00 - 16.00 WIB\n\nPendaftaran dan pemilihan tanggal dapat dilakukan dengan menghubungi hotline kami',
        'jadwal_audit' : '📅 Jadwal Pelatihan Audit Internal\n\nUjian terdekat akan diadakan pada:\n-6 Juli 2026 \n\nPendaftaran dan pemilihan tanggal dapat dilakukan dengan menghubungi hotline kami',
        'jadwal_financial' : '📅 Jadwal Basic Financial Modelling\n\nUjian terdekat akan diadakan pada:\n-7 September 2026 \n\nPendaftaran dan pemilihan tanggal dapat dilakukan dengan menghubungi hotline kami',
        'jadwal_erm' : '📅 Jadwal Pelatihan Enterprise Risk Management\n\nUjian akan terdekat diadakan pada:\n-14 September 2026\n Pukul 09.00 - 16.00 WIB \n\nPendaftaran dan pemilihan tanggal dapat dilakukan dengan menghubungi hotline kami',
        'jadwal_spc' : '📅 Jadwal Strategy, Performance, and Control Course\n\nUjian terdekat akan diadakan pada:\n-22 Agustus 2026\n Setiap Sabtu dan Minggu, pukul 09.00 - 15.00 WIB\n\nPendaftaran dan pemilihan tanggal dapat dilakukan dengan menghubungi hotline kami',
        'jadwal_gcrm' : '📅 Jadwal Governance, Control, and Risk Management\n\nUjian terdekat akan diadakan pada:\n-30 Mei 2026\n- 25 Juli 2026\n- 3 Oktober 2026\n Setiap Sabtu dan Minggu, pukul 09.00 - 15.00 WIB\n\nSilahkan memilih tanggal yang sesuai, pendaftaran dapat dilakukan dengan menghubungi hotline kami.',
        'jadwal_bcc' : '📅 Jadwal Budgeting and Cost Control Training\n\nUjian terdekat akan diadakan pada:\n- 20 Juni 2026\n Setiap Sabtu dan Minggu, pukul 18.30 - 21.00 WIB\n\nPendaftaran dan pemilihan tanggal dapat dilakukan dengan menghubungi hotline kami',
        'jadwal_excel' : '📅 Jadwal Advance Excel\n\nUjian terdekat akan diadakan pada:\n- 12 September 2026\n- 19 September 2026\n Sabtu dan Minggu, pukul 08.30 - 16.30 WIB\n\nSilahkan memilih tanggal yang sesuai, pendaftaran dapat dilakukan dengan menghubungi hotline kami.',
        'jadwal_facv' : '📅 Jadwal Financial Analysis and Corporate Valuation Workshop\n\nUjian terdekat akan diadakan pada:\n-15 Juni 2026 \n Setiap Senin sd Kamis, pukul 18.30 - 21.00 WIB\n\nPendaftaran dan pemilihan tanggal dapat dilakukan dengan menghubungi hotline kami',
        'jadwal_psak' : '📅 Jadwal Pelatihan PSAK Komprehensif\n\nUjian terdekat akan diadakan pada:\n-26 Mei 2026\n- 22 Desember 2026\n Setiap Selasa sd Kamis, pukul 18.30 - 21.00 WIB\n\nSilahkan memilih tanggal yang sesuai, pendaftaran dapat dilakukan dengan menghubungi hotline kami.',
        'jadwal_lapkeuangan' : '📅 Jadwal Bimtek Penyusunan Laporan Keuangan Pemerintah Daerah\n\nUjian terdekat akan diadakan pada:\n-14 Juli 2026\n- 14 Desember 2026\n Selasa sd Kamis, pukul 08.00 - 16.00 WIB\n\nSilahkan memilih tanggal yang sesuai, pendaftaran dapat dilakukan dengan menghubungi hotline kami.',
        'jadwal_keudaerah' : '📅 Jadwal Bimtek Keuangan Daerah Terpadu\n\nUjian terdekat akan diadakan pada:\n- 21 Juli 2026\n Selasa sd Kamis, pukul 09.00 - 16.00 WIB\n\nPendaftaran dan pemilihan tanggal dapat dilakukan dengan menghubungi hotline kami',
        'jadwal_pbmn' : '📅 Jadwal Bimtek Pengelolaan Barang Milik Negara/Daerah\n\nUjian terdekat akan diadakan pada:\n-18 Agustus 2026\n- 1 September\n Selasa dan Rabu, pukul 08.00 - 16.00 WIB\n\nSilahkan memilih tanggal yang sesuai, pendaftaran dapat dilakukan dengan menghubungi hotline kami.',
        'jadwal_retribusi' : '📅 Jadwal Bimtek Pajak dan Retribusi Daerah\n\nUjian terdekat akan diadakan pada:\n- 11 Agustus 2026\n Selasa sd Kamis, pukul 08.00 - 16.00 WIB\n\nPendaftaran dan pemilihan tanggal dapat dilakukan dengan menghubungi hotline kami',
        'jadwal_pembukuan' : '📅 Jadwal Pelatihan Pembukuan, Inventarisasi, dan Pelaporan Barang Milik Daerah\n\nSaat ini jadwal pelatihan belum tersedia 😊\n Namun, Anda masih dapat melakukan pendaftaran dan berdiskusi terkait penentuan jadwal dengan menghubungi hotline kami. Silahkan ketik "Kontak" atau pilih menu "Kontak Kami".',
        'jadwal_cgaa' : '📅 Jadwal CGAA review\n\nUjian terdekat akan diadakan pada:\n-21 September 2026\n- 28 Desember 2026\nSenin sd Kamis, pukul 09.00 - 16.00 WIB\n\nSilahkan memilih tanggal yang sesuai, pendaftaran dapat dilakukan dengan menghubungi hotline kami.',
        'jadwal_cgae' : '📅 Jadwal CGAE review\n\nUjian terdekat akan diadakan pada:\n-5 Oktober 2026\n- 19 Oktober 2026\nSenin sd Kamis, pukul 09.00 - 16.00 WIB\n\nSilahkan memilih tanggal yang sesuai, pendaftaran dapat dilakukan dengan menghubungi hotline kami.',
        'jadwal_blud' : '📅 Jadwal Pelatihan Penyusunan Laporan Keuangan BLUD Puskesmas\n\nSaat ini jadwal pelatihan belum tersedia 😊\n Namun, Anda masih dapat melakukan pendaftaran dan berdiskusi terkait penentuan jadwal dengan menghubungi hotline kami. Silahkan ketik "Kontak" atau pilih menu "Kontak Kami".',
        "biaya_cpsak": "💰 Biaya CPSAK Review\n\nRp6.000.000 per peserta\n\nBenefit:\n✅ Materi lengkap dan sesuai dengan silabus ujian CPSAK\n✅ Sertifikat\n✅ 13x pertemuan\n✅ Rekaman pelatihan\n✅ Dibimbing oleh profesional\n\nSilakan menghubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.",
        "biaya_usas": "💰 Biaya USAS Review\n\nRp2.000.000 per peserta\n\nBenefit:\n✅ Materi lengkap\n✅ Pemahaman laporan keuangan berdasarkan SAK syariah\n✅ Persiapan sebelum mengikuti sertifikasi\n✅ 2x pertemuan\n✅ Rekaman pelatihan\n✅ Dibimbing oleh profesional\n\nSilakan menghubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.",
        "biaya_crmo": "💰 Biaya CRMO Review\n\nRp3.500.000 per peserta\n\nBenefit:\n✅ Penguasaan teknik dan manajemen risiko\n✅ Persiapan sebelum mengikuti CRMO\n✅ 3x pertemuan\n✅ Rekaman pelatihan\n\nSilakan menghubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.",
        "biaya_csrs": "💰 Biaya CSRS Review\n\nRp4.000.000 per peserta\n\nBenefit:\n✅ Materi lengkap prinsip dan konsep dasar CSR\n✅ Modul penilaian dan pelaporan CSR\n✅ 4x pertemuan\n✅ Rekaman pelatihan\n✅ Latihan & pembahasan soal\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.",
        "biaya_brevet": "💰 Biaya Brevet A&B Terpadu\n\nRp2.000.000 per peserta\n\nBenefit:\n✅ Materi lengkap\n✅ 38x pertemuan\n✅ Dibimbing trainer ahli dibidangnya\n✅ Rekaman pelatihan\n✅ Problem solving berbasis studi\n✅ Transkrip nilai\n\nSilahkan Hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.",
        "biaya_cpma": "💰 Biaya CPMA Review\n\nRp6.000.000 per peserta\n\nBenefit:\n✅ 12x pertemuan\n✅ Latihan & Pembahasan Soal\n✅ Modul lengkap\n✅ Rekaman pelatihan\n✅ Dibimbing trainer berpengalaman\n\nSilakan menghubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.",
        "biaya_analyst": "💰 Biaya Pelatihan Data Analyst\n\nRp1.500.000 per peserta\n\nBenefit:\n✅ 4x pertemuan\n✅ Rekaman pelatihan\n✅ Modul lengkap\n✅ Latihan & pembahasan soal\n✅ Pemahaman modeling dan visualisasi data\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.",
        'biaya_ca': '💰 Biaya CA review\n\nRp7.200.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 14x pertemuan (28 sesi)\n✅ Trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n✅ Latihan & Pembahasan soal\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.',
        'biaya_cpa': '💰 Biaya CPA review\n\nRp6.500.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 14x pertemuan (28 sesi)\n✅ E-Sertifikat ber-SKP\n✅ Peluang karir di bidang industri, pemerintahan maupun kantor akuntan publik\n✅ Latihan & Pembahasan soal\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.',
        'biaya_uskp': '💰 Biaya USKP review\n\nRp2.400.000 - 3.300.000 per peserta *tergantung USKP yang dipilih\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ Dibimbing trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n✅ Latihan & Pembahasan soal\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk mahasiswa dan alumni Unair.',
        'biaya_basic_accounting': '💰 Biaya Pelatihan Basic Accounting\n\nRp2.000.000(Online) & Rp2.500.000(Offline) per peserta\n\nBenefit:\n✅ Modul & materi lengkap\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 28x pertemuan\n✅ Dibimbing oleh profesional\n✅ Latihan & Pembahasan soal\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 3 peserta.',
        'biaya_manajemen_risiko': '💰 Biaya Pelatihan Memahami Dasar-Dasar Manajemen Risiko\n\nRp1.200.000 per peserta\n\nBenefit:\n✅ Modul & materi lengkap\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ Trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n✅ Latihan & Pembahasan soal\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 3 peserta.',
        'biaya_audit': '💰 Biaya Pelatihan Audit Internal\n\nRp900.000 per peserta\n\nBenefit:\n✅ Soft file materi\n✅ E-Sertifikat\n✅ Rekaman pelatihan\n✅ 2x pertemuan\n✅ Speaker berpengalaman\n✅ Pemahaman audit sesuai standar audit internal global\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 3 peserta.',
        'biaya_financial': '💰 Biaya Basic Financial Modelling\n\nRp3.250.000 per peserta\n\nBenefit:\n✅ Soft file materi\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 2x pertemuan\n✅ Trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n✅ Latihan & Pembahasan soal\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 3 peserta.',
        'biaya_erm': '💰 Biaya Pelatihan Enterprise Risk Management\n\nRp1.000.000 per peserta\n\nBenefit:\n✅ Materi lengkap\n✅ Speaker berpengalaman\n✅ Rekaman pelatihan\n✅ 2x pertemuan\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 3 peserta.',
        'biaya_spc': '💰 Biaya Strategy, Performance, and Control Course\n\nRp7.500.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 6x pertemuan\n✅ Problem solving berbasis studi kasus\n✅ Trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n✅ Latihan & Pembahasan soal\n\nSilahkan hubungi admin untuk informasi lebih lanjut.',
        'biaya_gcrm': '💰 Biaya Governance, Control, and Risk Management\n\nRp6.000.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 14x pertemuan\n✅ Trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n✅ Latihan & Pembahasan soal\n\nSilahkan hubungi admin untuk informasi lebih lanjut.',
        'biaya_bcc': '💰 Biaya Budgeting and Cost Control Training\n\nRp1.500.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 4x pertemuan\n✅ Trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n✅ Problem solving berbasis studi kasus\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.',
        'biaya_excel': '💰 Biaya Advance Excel\n\nRp500.000 per peserta\n\nBenefit:\n✅ Materi lengkap\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 2x pertemuan (6 sesi)\n✅ Dibimbing oleh profesional\n✅ E-Sertifikat ber-SKP\n✅ Pemahaman pembuatan dashboard\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.',
        'biaya_facv': '💰 Biaya Financial Analysis and Corporate Valuation Workshop\n\nRp2.000.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 8x pertemuan\n✅ Trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n✅ Latihan & Pembahasan soal\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.',
        'biaya_psak': '💰 Biaya Pelatihan PSAK Komprehensif\n\nRp2.200.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 6x pertemuan\n✅ Trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n✅ Latihan & Pembahasan soal\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.',
        'biaya_lapkeuangan': '💰 Biaya Bimtek Penyusunan Laporan Keuangan Pemerintah Daerah\n\nRp2.000.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 3x pertemuan (9 sesi)\n✅ Trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n✅ Problem solving berbasis studi kasus\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.',
        'biaya_keudaerah': '💰 Biaya Bimtek Keuangan Daerah Terpadu\n\nRp3.500.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Materi lengkap\n✅ Rekaman pelatihan\n✅ 3x pertemuan(Online/Offline)\n✅ Trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 3 peserta.',
        'biaya_pbmn': '💰 Biaya Bimtek Pengelolaan Barang Milik Negara/Daerah\n\nRp2.250.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 2x pertemuan\n✅ Trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n✅ Latihan & Pembahasan soal\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.',
        'biaya_retribusi': '💰 Biaya Bimtek Pajak dan Retribusi Daerah\n\nRp2.250.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 3x pertemuan (9 sesi)\n✅ Dibimbing oleh Ahli\n✅ E-Sertifikat ber-SKP\n✅ Problem solving berbasis studi kasus\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.',
        'biaya_pembukuan': '💰 Biaya Pelatihan Pembukuan, Inventarisasi, dan Pelaporan Barang Milik Daerah\n\nRp2.250.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 2x pertemuan (6 sesi)\n✅ Trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n✅ Problem solving berbasis studi kasus\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.',
        'biaya_cgaa': '💰 Biaya CGAA review\n\nRp1.750.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 4x pertemuan (8 sesi)\n✅ Trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n✅ Latihan & Pembahasan soal\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.',
        'biaya_cgae': '💰 Biaya CGAE review\n\nRp1.750.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 4x pertemuan (8 sesi)\n✅ Trainer berpengalaman\n✅ E-Sertifikat ber-SKP\n✅ Latihan & Pembahasan soal\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.',
        'biaya_blud': '💰 Biaya Pelatihan Penyusunan Laporan Keuangan BLUD Puskesmas\n\nRp2.500.000 per peserta\n\nBenefit:\n✅ Modul\n✅ Transkrip nilai\n✅ Rekaman pelatihan\n✅ 3x pertemuan (9 sesi)\n✅ Dibimbing oleh profesional\n✅ E-Sertifikat ber-SKP\n✅ Pemahaman penyusunan laporan sesuai SAP\n\nSilahkan hubungi admin untuk informasi lebih lanjut. Tersedia potongan harga khusus untuk pendaftaran kolektif minimal 4 peserta.',
        "cara_daftar": "📝 Cara Pendaftaran\n\n1. Isi formulir online\n2. Upload dokumen\n3. Bayar biaya pendaftaran\n4. Konfirmasi pembayaran\n5. Join grup whatsapp untuk informasi lebih lanjut\n\n📱 Daftar di: lppapsi.unair.ac.id",
        "kontak": "📞 Kontak Kami\n\n📧 Email: lppapsi@feb.unair.ac.id\n📱 Telepon:\n  • Karina: 082338829782\n  • Nisa: 08563058535\n  • Halimah: 081252675245\n  • Mufa: 08125990311\n📍 Alamat: Kampus B Universitas Airlangga, Jl. Airlangga No. 4-6 Surabaya, 60628\n🕐 Senin-Jumat: 09.00-16.00"
    }
    
    return responses_map.get(callback, "Silakan pilih menu yang tersedia.")

# =====================
# ANALYTICS TRACKING - UNCHANGED
# =====================
analytics = {
    "total_messages": 0,
    "menu_clicks": {},
    "entities_extracted": [],
    "quick_search_hits": 0
}

def track_analytics(message_type, data):
    """Track user interactions for analytics"""
    analytics["total_messages"] += 1
    
    if message_type == "menu_click":
        callback = data.get("callback")
        analytics["menu_clicks"][callback] = analytics["menu_clicks"].get(callback, 0) + 1
    elif message_type == "entity_extraction":
        analytics["entities_extracted"].append({
            "timestamp": datetime.now().isoformat(),
            "entities": data
        })
    elif message_type == "quick_search":
        analytics["quick_search_hits"] += 1

# =====================
# API ENDPOINTS - UNCHANGED STRUCTURE
# =====================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")
        
        # Track analytics
        track_analytics("message", {"text": user_message})
        
        # Generate response
        reply = get_response(user_message)
        
        # Extract entities for analytics
        entities = extract_entities(user_message)
        track_analytics("entity_extraction", entities)
        
        # Track if quick search was used
        if entities["program_name"] and entities["intent"] in ["biaya", "jadwal"]:
            track_analytics("quick_search", {"program": entities["program_name"]})
        
        # Get appropriate menu buttons
        buttons = MENU_BUTTONS["main"]
        
        return jsonify({
            "reply": reply,
            "buttons": buttons,
            "entities": entities,
            "timestamp": datetime.now().strftime("%H:%M")
        })
    except Exception as e:
        return jsonify({
            "reply": "Maaf, terjadi kesalahan. Silakan coba lagi.",
            "buttons": MENU_BUTTONS["main"],
            "error": str(e)
        }), 500

@app.route("/menu_click", methods=["POST"])
def menu_click():
    try:
        data = request.json
        callback = data.get("callback", "")
        
        # Track analytics
        track_analytics("menu_click", {"callback": callback})
        
        # Handle main menu callback

        if callback == "all_programs":
            return jsonify({
                "reply": generate_program_list(),
                "buttons": MENU_BUTTONS["main"],
                "timestamp": datetime.now().strftime("%H:%M")
            })

        elif callback == "biaya_menu":
            return jsonify({
                "reply": "Pilih kategori untuk melihat biaya pelatihan:",
                "buttons": [
                    {"text": "🏢 Pelatihan Perusahaan", "callback": "kategori_perusahaan"},
                    {"text": "🎓 Sertifikasi Profesional", "callback": "kategori_sertifikasi"},
                    {"text": "🏛️ Pelatihan Pemerintah", "callback": "kategori_pemerintah"},
                    {"text": "🔙 Menu Utama", "callback": "main_menu"},
                ],
                "timestamp": datetime.now().strftime("%H:%M")
            })
        
        elif callback == "jadwal_menu":
            return jsonify({
                "reply": "📅 Pilih kategori untuk melihat jadwal pelatihan:",
                "buttons": [
                    {"text": "🏢 Pelatihan Perusahaan", "callback": "kategori_perusahaan_jadwal"},
                    {"text": "🎓 Sertifikasi Profesional", "callback": "kategori_sertifikasi_jadwal"},
                    {"text": "🏛️ Pelatihan Pemerintah", "callback": "kategori_pemerintah_jadwal"},
                    {"text": "🔙 Menu Utama", "callback": "main_menu"},
                ],
                "timestamp": datetime.now().strftime("%H:%M")
            }) 

        if callback == "main_menu":
            return jsonify({
                "reply": "🏠 Menu Utama\n\n👋 Halo saya Chatbot LPPAPSI UNAIR!\nSaya siap membantu Anda 😊\nSilakan pilih menu di bawah ini:",
                "buttons": MENU_BUTTONS["main"],
                "timestamp": datetime.now().strftime("%H:%M")
            })
        elif callback == "all_programs":
            return generate_program_list()
        # elif callback == "biaya_menu":
        #     return "💰 **Informasi Biaya Pelatihan**\n\nSilakan pilih kategori pelatihan untuk melihat biaya:\n\n🏢 Pelatihan Perusahaan\n🎓 Sertifikasi Profesional\n🏛️ Pelatihan Pemerintah"
            
        
        # Get menu for this callback
        if callback in MENU_BUTTONS:
            buttons = MENU_BUTTONS[callback]
            
            # Custom titles for categories
            category_titles = {
                "kategori_perusahaan": "🏢 Pelatihan Perusahaan\n\nPilih program:",
                "kategori_sertifikasi": "🎓 Sertifikasi Profesional\n\nPilih program:",
                "kategori_pemerintah": "🏛️ Pelatihan Pemerintah\n\nPilih program:",
                "info_kontak": "📞 Informasi\n\nApa yang ingin Anda ketahui?"
            }
            
            reply = category_titles.get(callback, "Silakan pilih:")
        else:
            # Get response for this callback
            reply = handle_menu_callback(callback)
            
            # Determine which menu to show back
            if callback.startswith("biaya_") or callback.startswith("jadwal_"):
                # Determine category based on callback
                perusahaan_programs = ["basic_accounting", "manajemen_risiko", "audit", "brevet", "financial", "erm"]
                sertifikasi_programs = ["cpsak", "usas", "crmo", "csrs", "analyst", "ca", "cpa", "uskp"]
                pemerintah_programs = ["lapkeuangan", "keudaerah", "pbmn", "retribusi", "cgaa", "cgae", "blud"]
                
                prog_name = callback.replace("biaya_", "").replace("jadwal_", "")
                
                if any(p in callback for p in perusahaan_programs):
                    buttons = MENU_BUTTONS["kategori_perusahaan"]
                elif any(p in callback for p in sertifikasi_programs):
                    buttons = MENU_BUTTONS["kategori_sertifikasi"]
                elif any(p in callback for p in pemerintah_programs):
                    buttons = MENU_BUTTONS["kategori_pemerintah"]
                else:
                    buttons = MENU_BUTTONS["main"]
            elif callback in ["kontak", "cara_daftar"]:
                buttons = MENU_BUTTONS["info_kontak"]
            else:
                # buttons = MENU_BUTTONS["main"]
                reply = "👋 Halo! Saya ChatBot LPPAPSI\n\nSilakan pilih menu di bawah ini:"
                buttons = MENU_BUTTONS["main"]
        
        return jsonify({
            "reply": reply,
            "buttons": buttons,
            "timestamp": datetime.now().strftime("%H:%M")
        })
    except Exception as e:
        return jsonify({
            "reply": "Maaf, terjadi kesalahan.",
            "buttons": MENU_BUTTONS["main"],
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) 
