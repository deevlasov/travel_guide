import Stripe from 'stripe';

const isProd = process.env.VERCEL_ENV === 'production';

const stripeSecretKey = isProd
  ? process.env.STRIPE_SECRET_KEY
  : process.env.STRIPE_SECRET_KEY_TEST;

const endpointSecret = isProd
  ? process.env.STRIPE_WEBHOOK_SECRET
  : process.env.STRIPE_WEBHOOK_SECRET_TEST;

const stripe = new Stripe(stripeSecretKey);

export const config = {
  api: {
    bodyParser: false, // Stripe requires the raw body
  },
};

export default async function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).end('Method Not Allowed');
    return;
  }

  const buf = await new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', (chunk) => chunks.push(chunk));
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });

  let event;
  try {
    event = stripe.webhooks.constructEvent(buf, req.headers['stripe-signature'], endpointSecret);
  } catch (err) {
    res.status(400).send(`Webhook Error: ${err.message}`);
    return;
  }

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    const email = session.customer_details?.email;
    const phone = session.customer_details?.phone;
    const name = session.customer_details?.name;
    const product = session.metadata?.product || 'Travel Guide';

    // Call your add-customer endpoint
    await fetch('https://travel-guide-vert-two.vercel.app/api/add-customer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, phone, product }),
    });
  }

  res.status(200).json({ received: true });
} 