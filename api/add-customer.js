import { Client } from "@notionhq/client";

const notion = new Client({ auth: process.env.NOTION_TOKEN });
const databaseId = process.env.NOTION_DATABASE_ID;

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end();

  const { name, email, phone, product } = req.body;
  if (!email) return res.status(400).json({ error: "Missing email" });

  try {
    await notion.pages.create({
      parent: { database_id: databaseId },
      properties: {
        Name: { title: [{ text: { content: name || "" } }] },
        Email: { email: email },
        Phone: { phone_number: phone || "" },
        Product: { rich_text: [{ text: { content: product || "" } }] }
      }
    });
    res.status(200).json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
} 