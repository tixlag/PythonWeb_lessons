//Задание 1
const defaultUser = {
  name: "Anonymous",
  contacts: { email: "no-email@example.com" },
  settings: { theme: "light", lang: "en" },
};

const rawUsers = [
  { name: "Alice", contacts: { email: "alice@mail.com" }, settings: { theme: "dark" } },
  { contacts: {}, settings: null },
  { name: "", settings: { lang: "ru" } },    
];

function normalizeUser(raw, defaults) {
  const normalized = {
    name: raw.name ?? defaults.name,

    contacts: {
      ...defaults.contacts,
      email: raw.contacts?.email ?? defaults.contacts.email,
    },

    settings: {
      ...defaults.settings,
      theme: raw.settings?.theme ?? defaults.settings.theme,
      lang: raw.settings?.lang ?? defaults.settings.lang,
    },
  };

  console.log('name: ${typeof normalized.name}');
  console.log('contacts: ${typeof normalized.contacts}');
  console.log('settings: ${typeof normalized.settings}');

  return normalized;
};

console.log('=== Результаты нормализации ===');
const normalizedUsers = rawUsers.map(raw => normalizeUser(raw, defaultUser));

normalizedUsers.forEach((user, index) => {
  console.log(`Пользователь ${index + 1}:`, JSON.stringify(user, null, 2));
  console.log();
});


//Задание 2
const cart = [
  { title: "Keyboard", price: 3000, category: "tech" },
  { title: "Coffee", price: "450", category: "food" },  // строка!
  { title: "Monitor", price: 12000, category: "tech" },
  { title: "Mystery box", category: "other" },          // цены нет!
  { title: "Sticker", price: 0, category: "other" },    // нулевая цена — валидна
];

function toNumberPrice(item) {
  const newItem = {...item};
  const priceAsNumber = Number(newItem.price);

  if (typeof priceAsNumber === 'number') {
    newItem.price = priceAsNumber;
  } else {
    newItem.price = null;
  }
  return newItem;
}

const applyDiscount = (price, discount = 10) => {
  return price * (1 - discount / 100);
};

const normalizedCart = cart.map(toNumberPrice);

const report = {
  validItems: normalizedCart.filter(item => typeof item.price === 'number' && item.price !== null),

  techItems: normalizedCart.filter(item => item.category === 'tech'),

  discountedTotal: normalizedCart 
    .filter(item => typeof item.price === 'number' && item.price !== null)
    .map(item => applyDiscount(item.price))
    .reduce((sum, discountedPrice) => sum + discountedPrice, 0),

  maxPriceItemTitle: normalizedCart
    .filter(item => typeof item.price === 'number' && item.price !== null)
    .reduce((maxItem, currentItem) => {
      if (!maxItem || currentItem.price > maxItem.price) {
        return currentItem;
      }
      return maxItem;
    }, null)?.title || "Нет товаров" 
};



//Задание 3
const steps = [
  { label: "warmup", ms: 300 },
  { label: "work", ms: 600 },
  { label: "cooldown", ms: 300 },
];

function delay(ms) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(); 
    }, ms);
  });
}

async function runSteps(steps) {
  const completedLabels = [];
  for (const step of steps) {
    try {
      if (typeof step.ms !== 'number' || step.ms < 0) {
        throw new Error(`Ошибка мс в шаге "${step.label}": ${step.ms}`);
      }
      console.log(`Start ${step.label}`);

      await delay(step.ms);

      console.log(`End ${step.label}`);

      completedLabels.push(step.label);

    } catch (error) {
      console.error(`Ошибка в шаге "${step.label}":`, error.message);
      break;
    }
  } 
  return completedLabels;
}