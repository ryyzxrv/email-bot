import makeWASocket, { useMultiFileAuthState, DisconnectReason } from "@whiskeysockets/baileys";
import Pino from "pino";
import fs from "fs";
import axios from "axios";
import chalk from "chalk";
import config from "./config.js";

let waClient = null;

async function startWhatsAppClient() {
  console.log(chalk.cyan("🔄 Menghubungkan ke WhatsApp..."));
  const { state, saveCreds } = await useMultiFileAuthState(config.sessionName);

  waClient = makeWASocket({
    printQRInTerminal: true,
    browser: ["Ubuntu", "Chrome", "110.0"],
    logger: Pino({ level: "silent" }),
    auth: state,
  });

  waClient.ev.on("creds.update", saveCreds);

  waClient.ev.on("connection.update", ({ connection, lastDisconnect }) => {
    if (connection === "close") {
      const reason = lastDisconnect?.error?.output?.statusCode;
      if (reason !== DisconnectReason.loggedOut) {
        console.log(chalk.yellow("⚠️ Terputus, mencoba ulang..."));
        startWhatsAppClient();
      } else {
        console.log(chalk.red("❌ Logout. Hapus session dan scan ulang."));
      }
    } else if (connection === "open") {
      console.log(chalk.green("✅ Berhasil tersambung ke WhatsApp!"));
    }
  });
}

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
