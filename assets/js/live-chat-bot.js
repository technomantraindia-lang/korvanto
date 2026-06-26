/**
 * Korvanto Live Chat Assistant — conversational B2B export support.
 */
(function (global) {
  'use strict';

  function pick(list) {
    return list[Math.floor(Math.random() * list.length)];
  }

  function normalize(text) {
    return (text || '')
      .toLowerCase()
      .replace(/['']/g, "'")
      .replace(/\s+/g, ' ')
      .trim();
  }

  function has(text, pattern) {
    return pattern.test(text);
  }

  var OPENERS = [
    'Sure — ',
    'Got it — ',
    'Happy to help — ',
    'Of course — ',
    'Thanks for asking — '
  ];

  var EMAIL = 'exports@korvanto.com';
  var PHONE = '+91 90540 07999';

  function createSession() {
    return {
      name: '',
      product: '',
      application: '',
      quantity: '',
      destination: '',
      turn: 0
    };
  }

  function KorvantoLiveChat() {
    var session = createSession();

    function greetName() {
      return session.name ? session.name + ', ' : '';
    }

    function isOrderIntent(text) {
      return has(
        text,
        /(?:place|give|make|book|submit|confirm|start|proceed with|ready for)\s+(?:an?\s+)?order|want\s+to\s+(?:place\s+)?(?:an?\s+)?order|want\s+to\s+(?:buy|purchase)|want\s+order|need\s+to\s+order|like\s+to\s+order|order\s+now|place\s+my\s+order|send\s+order|finalize\s+order|finalise\s+order|i\s+want\s+to\s+buy|ready\s+to\s+buy/
      );
    }

    function isQuoteIntent(text) {
      return has(text, /\b(quote|quotation|pricing|price|cost|rate|how much)\b/);
    }

    function isFollowUp(text) {
      if (isOrderIntent(text) || isQuoteIntent(text)) return false;
      if (has(text, /^(hi|hello|hey|help|what|which|tell|show|list|who|where|how)\b/)) return false;
      return text.length < 80;
    }

    function matchesProductTopic(text, pattern, appKey) {
      return has(text, pattern) || (session.application === appKey && isFollowUp(text));
    }

    function extractDetails(text) {
      if (has(text, /\b(\d+)\s*(mt|ton|tons|tonne|tonnes|kg|container|fcl|lcl)\b/)) {
        session.quantity = text.match(/\b(\d+\s*(?:mt|ton|tons|tonne|tonnes|kg|container|fcl|lcl)s?)\b/i)[0];
      }
      if (has(text, /\bto\s+([a-z][a-z\s]{2,30})\b/)) {
        var dest = text.match(/\bto\s+([a-z][a-z\s]{2,30})\b/i);
        if (dest) session.destination = dest[1].trim();
      }
      if (has(text, /\bmy name is\s+([a-z][a-z\s'-]{1,30})\b/i)) {
        session.name = text.match(/\bmy name is\s+([a-z][a-z\s'-]{1,30})\b/i)[1].trim();
      }
    }

    function productFamiliesReply() {
      return (
        pick(OPENERS) +
        'Korvanto supplies 7 branded mineral families:\n\n' +
        '• KORVANTO BENTO™ — drilling, foundry, civil, feed, fertilizer & specialty grades\n' +
        '• KORVANTO KAO™ — crude, levigated, hydrous, calcined & metakaolin\n' +
        '• KORVANTO CLAY™ — ball clay for ceramics\n' +
        '• KORVANTO LAT™ — laterite for cement & construction\n' +
        '• KORVANTO CHAM™ — refractory chamotte\n' +
        '• KORVANTO BAUX™ — calcined bauxite\n' +
        '• KORVANTO CARBO™ — lustrous carbon for foundry\n\n' +
        'Which mineral and application are you sourcing for?'
      );
    }

    function quoteReply() {
      var parts = [];
      if (session.product) parts.push('Product: ' + session.product);
      if (session.quantity) parts.push('Quantity: ' + session.quantity);
      if (session.destination) parts.push('Destination: ' + session.destination);

      if (parts.length >= 2) {
        return (
          pick(OPENERS) +
          greetName() +
          "I have your key details (" +
          parts.join('; ') +
          "). Our export desk will prepare a formal quotation with grade, packaging, and Incoterms.\n\n" +
          'For fastest response, submit our Request a Quote form or email ' +
          EMAIL +
          ' with your company name and specifications.'
        );
      }

      return (
        pick(OPENERS) +
        'To prepare an accurate export quotation, please share:\n' +
        '1. Product & grade (e.g. API bentonite, F-200 foundry)\n' +
        '2. Monthly or trial quantity\n' +
        '3. Packaging preference (25 kg, 50 kg, FIBC)\n' +
        '4. Destination port / country\n\n' +
        'You can also use our Request a Quote page on the website.'
      );
    }

    function orderReply() {
      return (
        pick(OPENERS) +
        greetName() +
        "great — let's get your order started.\n\n" +
        'Please confirm: product & grade, quantity, packaging, destination port, and your company name. ' +
        'Our team will share proforma invoice, COA approach, and dispatch timeline.\n\n' +
        'Email: ' +
        EMAIL +
        ' | Phone/WhatsApp: ' +
        PHONE
      );
    }

    function contactReply() {
      return (
        'You can reach Korvanto directly:\n\n' +
        '📧 ' +
        EMAIL +
        '\n📞 ' +
        PHONE +
        '\n📍 304, The City Centre, Raiya Road, Rajkot, Gujarat, India\n\n' +
        'Office hours: Mon–Sat, 9:30 AM – 6:30 PM IST'
      );
    }

    function docsReply() {
      return (
        pick(OPENERS) +
        'we provide full export documentation:\n' +
        '• Technical Data Sheet (TDS)\n' +
        '• Certificate of Analysis (COA)\n' +
        '• MSDS / SDS\n' +
        '• Samples & third-party testing on request\n\n' +
        'Share the product grade and destination — we will confirm document set for your market.'
      );
    }

    function shippingReply() {
      return (
        pick(OPENERS) +
        'Korvanto ships globally from India with:\n' +
        '• 25 kg / 50 kg bags, FIBC jumbo bags, palletized & containerized loads\n' +
        '• FOB, CIF, CNF and other B2B Incoterms\n' +
        '• Trial loads and full container programmes\n\n' +
        'Tell us product, quantity, and destination port for a logistics plan.'
      );
    }

    function welcome() {
      return pick([
        'Hello! I am Riya from Korvanto export support. How can I help with industrial minerals today?',
        'Welcome to Korvanto! Ask about bentonite, kaolin, refractories, quotes, or export documentation.',
        'Hi there! Tell me the mineral you need, quantity, and destination — or pick a quick topic below.'
      ]);
    }

    function fallback() {
      session.turn += 1;
      if (session.turn > 2) {
        return (
          "I want to make sure you get the right answer. For detailed enquiries, email " +
          EMAIL +
          ' or WhatsApp ' +
          PHONE +
          '. You can also request a callback from the contact menu.'
        );
      }
      return (
        pick(OPENERS) +
        'could you share a bit more? For example: product type, application, quantity, and destination country. ' +
        'Or ask about products, quotes, documents, or shipping.'
      );
    }

    function reply(userText) {
      var text = normalize(userText);
      if (!text) return welcome();

      extractDetails(text);
      session.turn += 1;

      if (/^(hi|hello|hey|good\s*(morning|afternoon|evening)|namaste)\b/.test(text)) {
        return welcome();
      }

      if (isOrderIntent(text)) {
        return orderReply();
      }

      if (isQuoteIntent(text)) {
        return quoteReply();
      }

      if (has(text, /\b(contact|email|phone|call|address|reach|whatsapp)\b/)) {
        return contactReply();
      }

      if (has(text, /\b(tds|coa|msds|sds|document|certificate|sample|testing)\b/)) {
        return docsReply();
      }

      if (has(text, /\b(ship|shipping|packag|fob|cif|incoterm|container|export|logistics|delivery)\b/)) {
        return shippingReply();
      }

      if (
        has(text, /\b(product|grade|catalogue|catalog|list|supply|mineral|families|what do you)\b/) ||
        has(text, /\b(bentonite|kaolin|ball clay|laterite|chamotte|bauxite|metakaolin|carbo)\b/)
      ) {
        if (matchesProductTopic(text, /\b(drill|api|ocma|hdd|piling)\b/, 'drill')) {
          session.application = 'drill';
          session.product = 'KORVANTO BENTO DRILL';
          return (
            pick(OPENERS) +
            'KORVANTO BENTO DRILL covers API, OCMA+, and OCMA grades for oil & gas, water well, HDD, and geotechnical drilling.\n\n' +
            'API: dial reading ≥30, filtrate ≤15 cm³\nOCMA+: yield ratio ≤6, filtrate ≤16 cm³\n\n' +
            'Share borehole type, mud system, and monthly volume for grade recommendation.'
          );
        }

        if (matchesProductTopic(text, /\bfoundry|green sand|molding\b/, 'foundry')) {
          session.application = 'foundry';
          session.product = 'KORVANTO BENTO FOUNDRY';
          return (
            pick(OPENERS) +
            'KORVANTO BENTO FOUNDRY grades F-100 and F-200 are for green sand molding — grey iron, ductile iron, steel, and non-ferrous castings.\n\n' +
            'F-100: swelling 28–30 ml, MBV ~390\nF-200: swelling 32 ml, higher gelling index\n\n' +
            'What casting line and monthly tonnage are you running?'
          );
        }

        if (has(text, /\bkaolin|china clay|metakaolin|calcined kaolin\b/)) {
          session.product = 'KORVANTO KAO';
          return (
            pick(OPENERS) +
            'KORVANTO KAO™ includes crude, levigated noodles & lumps, hydrous, calcined, and metakaolin for ceramics, paints, paper, plastics, and construction.\n\n' +
            'Which form and application do you need — e.g. ceramic body, coating, or pozzolanic concrete?'
          );
        }

        return productFamiliesReply();
      }

      if (has(text, /\b(thanks|thank you|ok|okay|bye|goodbye)\b/)) {
        return pick([
          "You're welcome! Reach us anytime at " + EMAIL + '.',
          'Happy to help. Our export team is available if you need a formal quotation.',
          "My pleasure. I'm here if you need more details on products or export."
        ]);
      }

      return fallback();
    }

    function reset() {
      session = createSession();
    }

    function typingLabel() {
      return pick(['Riya is typing…', 'Just a moment…', 'Checking details…']);
    }

    return {
      reply: reply,
      reset: reset,
      welcome: welcome,
      typingLabel: typingLabel
    };
  }

  global.KorvantoLiveChat = KorvantoLiveChat;
})(typeof window !== 'undefined' ? window : global);
