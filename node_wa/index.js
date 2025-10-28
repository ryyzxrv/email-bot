import { Client, LocalAuth } from "whatsapp-web.js";
import express from "express";
import fetch from "node-fetch";
import { telegramBotUrl } from "./config.js";

const app = express();
app.use(express.json());

// Inisialisasi client WA dengan LocalAuth (nyimpen sesi otomatis)
const client = new Client({
  authStrategy: new LocalAuth({ dataPath: "./session" }),
  webVersionCache: {
    type: "remote",
    remotePath:
      "https://raw.githubusercontent.com/wppconnect-team/wa-version/main/html/2.2410.1.html",
  },
});

// Saat butuh pairing code (buat login pertama kali)
client.on("qr", async (qr) => {
  console.log("📲 Scan QR Code / gunakan pairing code WhatsApp...");
});

// Kalau kamu mau pairing lewat kode (bukan QR)
client.on("ready", async () => {
  console.log("✅ WhatsApp berhasil tersambung!");
});

// Saat login berhasil
client.on("authenticated", () => {
  console.log("🔐 Autentikasi berhasil!");
});

// Saat logout
client.on("disconnected", (reason) => {
  console.log("❌ WhatsApp terputus:", reason);
});

// Endpoint buat cek status
app.get("/status", (req, res) => {
  res.json({ status: client.info ? "connected" : "disconnected" });
});

// Endpoint untuk kirim pesan dari Telegram ke WhatsApp
app.post("/send", async (req, res) => {
  const { number, message } = req.body;
  try {
    const chatId = number.replace(/\D/g, "") + "@c.us";
    await client.sendMessage(chatId, message);
    res.json({ success: true, msg: "Pesan terkirim ke WA" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, error: err.message });
  }
});

client.initialize();
app.listen(5000, () => console.log("🚀 Server jalan di http://localhost:5000"));
/**
 * Cek bio WA
 */
async function checkBio(numbers) {
  if (!waClient) throw new Error("WA belum tersambung!");
  const results = [];

  for (const num of numbers) {
    const jid = num + "@s.whatsapp.net";
    try {
      const status = await waClient.fetchStatus(jid);
      results.push({
        number: num,
        bio: status.status || "-",
        setAt: status.setAt ? new Date(status.setAt).toLocaleString() : "Unknown",
      });
    } catch (e) {
      results.push({ number: num, bio: "❌ Tidak terdaftar / error" });
    }
  }

  return results;
}

/**
 * Terima request dari Python via stdin
 */
process.stdin.on("data", async (data) => {
  const msg = data.toString().trim();
  const [cmd, ...args] = msg.split(" ");

  if (cmd === "checkbio") {
    try {
      const results = await checkBio(args);
      const outFile = `${config.hasilFolder}/hasil_${Date.now()}.txt`;
      const text = results
        .map(r => `📞 ${r.number}\n📝 ${r.bio}\n🕒 ${r.setAt}\n`)
        .join("\n------------------\n");
      fs.writeFileSync(outFile, text);
      console.log(chalk.green(`✅ Hasil disimpan di ${outFile}`));
    } catch (e) {
      console.error("Gagal cek bio:", e);
    }
  }
});

startWhatsAppClient();
