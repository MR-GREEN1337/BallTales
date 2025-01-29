export const languageContent = {
    en: {
      welcomeMessage: "Hey there! I'm your baseball buddy, here to chat about the game we love! 💫⚾️ Tell me, what got you into baseball?",
      pageTitle: "Welcome to BallTales",
      pageSubtitle: "Let's chat about baseball and get to know your interests",
      inputPlaceholder: "Type anything about baseball..."
    },
    es: {
      welcomeMessage: "¡Hola! Soy tu compañero de béisbol, ¡aquí para charlar sobre el juego que amamos! 💫⚾️ Cuéntame, ¿qué te hizo interesarte por el béisbol?",
      pageTitle: "Bienvenido a BallTales",
      pageSubtitle: "Hablemos de béisbol y conozcamos tus intereses",
      inputPlaceholder: "Escribe cualquier cosa sobre béisbol..."
    },
    ja: {
      welcomeMessage: "こんにちは！私はあなたの野球仲間です。大好きな野球について話しましょう！💫⚾️ 野球を好きになったきっかけを教えてください。",
      pageTitle: "BallTalesへようこそ",
      pageSubtitle: "野球について話して、あなたの興味を教えてください",
      inputPlaceholder: "野球について何でも入力してください..."
    }
  };

export const typingPhrases = {
    en: [
      "Thinking...",
      "Mulling it over...",
      "Processing..."
    ],
    es: [
      "Pensando...",
      "Reflexionando...",
      "Procesando..."
    ],
    ja: [
      "考え中...",
      "検討中...",
      "処理中..."
    ]
  };

  export const ENDPOINT_TITLES: Record<string, string> = {
    // Team endpoints
    '/api/team/games/recent': 'Recent Games',
    '/api/team/roster/current': 'Current Roster',
    '/api/team/roster/all-time': 'All-Time Roster',
    '/api/team/stats': 'Team Statistics',
    'championships': 'Championship History',
    
    // Player endpoints
    '/api/player/games/recent': 'Recent Games',
    '/api/player/stats': 'Player Statistics',
    '/api/player/awards': 'Awards & Achievements',
    '/api/player/highlights': 'Career Highlights',
    '/api/player/homeruns': 'Home Run Tracker'
  };

  export const getEndpointTitle = (endpoint: string): string => {
    return ENDPOINT_TITLES[endpoint] || 
      endpoint.split('/').pop()?.split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ') || 
      'Results';
  };