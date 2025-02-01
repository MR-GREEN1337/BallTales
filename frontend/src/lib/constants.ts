import { env } from "next-runtime-env";

export const languageContent = {
  en: {
    form: {
      passwordStrong: "Strong password!",
      passwordGettingThere: "Getting there...",
      passwordMakeStronger: "Make your password stronger",
      nameRequired: "Name is required",
      nameMinLength: "Name must be at least 2 characters",
      error: "Error",
      errorOccurred: "An error occurred"
    },
    welcome: {
      greeting: "Hey there! I'm your baseball buddy, here to chat about the game we love! 💫⚾️",
      initialQuestion: "Tell me, what got you into baseball?",
      pageTitle: "Welcome to BallTales",
      pageSubtitle: "Let's chat about baseball and get to know your interests",
      inputPlaceholder: "Type anything about baseball...",
      returnGreeting: "Welcome back to BallTales! Ready to talk more baseball? ⚾️"
    },
    auth: {
      welcomeBack: "Welcome Back",
      welcomeNew: "Welcome",
      signInContinue: "Sign in to continue to BallTales",
      signUpJoin: "Sign up to join BallTales",
      email: "Email",
      password: "Password",
      name: "Your name",
      rememberMe: "Remember me",
      signIn: "Sign In",
      signUp: "Sign Up",
      continue: "Continue",
      createAccount: "Create Account",
      selectLanguage: "Select language",
      noAccount: "Don't have an account?",
      haveAccount: "Already have an account?",
      forgotPassword: "Forgot password?",
      accountCreated: "Account created successfully!",
      passwordReset: "Password reset email sent",
      sessionExpired: "Your session has expired. Please sign in again.",
      verifyEmail: "Please verify your email address",
      resendVerification: "Resend verification email"
    },
    validation: {
      required: {
        email: "Email is required",
        password: "Password is required",
        name: "Name is required"
      },
      invalid: {
        email: "Please enter a valid email address",
        password: "Password must contain uppercase, lowercase, number, and special character",
        name: "Name must be at least 2 characters"
      },
      password: {
        tooShort: "Password is too short",
        makeStronger: "Make your password stronger",
        gettingThere: "Getting there...",
        strong: "Strong password!",
        requirements: "Must include: uppercase, lowercase, number, and special character",
        minLength: "Minimum 8 characters required",
        match: "Passwords must match"
      },
      name: {
        tooShort: "Name is too short",
        minLength: "Name must be at least 2 characters",
        maxLength: "Name cannot exceed 50 characters",
        invalid: "Name can only contain letters and spaces"
      }
    },
    profile: {
      baseballFan: "Baseball Fan",
      teamFanSuffix: "Fan",
      viewProfile: "View Profile",
      editProfile: "Edit Profile",
      uploadPhoto: "Upload Photo",
      analyzePhoto: "Analyze Photo"
    },
    statsSection: {
      title: "Baseball Stats",
      messagesExchanged: "Messages Exchanged",
      queriesAnswered: "Queries Answered",
      daysActive: "Days Active",
      gamesWatched: "Games Watched",
      predictions: "Predictions Made",
      accuracy: "Prediction Accuracy"
    },
    preferencesSection: {
      title: "Baseball Preferences",
      favoriteTeam: "Favorite Team",
      favoritePlayer: "Favorite Player",
      memorableHomeRun: "Most Memorable Home Run",
      favoriteStadium: "Favorite Stadium",
      preferredPosition: "Preferred Position",
      favoriteEra: "Favorite Baseball Era"
    },
    settings: {
      title: "Settings",
      language: "Language",
      theme: "Theme",
      notifications: "Notifications",
      statsPreference: "Stats Preference",
      notificationPreference: "Notification Preference",
      privacySettings: "Privacy Settings",
      dataPreferences: "Data Preferences"
    },
    actions: {
      signOut: "Sign Out",
      save: "Save Changes",
      cancel: "Cancel",
      confirm: "Confirm",
      edit: "Edit",
      delete: "Delete",
      view: "View Details"
    },
    notifications: {
      gameStart: "Game Starting Soon",
      scoreUpdate: "Score Update",
      playerStats: "Player Stats Update",
      teamNews: "Team News",
      matchPrediction: "Match Prediction Available"
    },
    errors: {
      loadFailed: "Failed to load profile",
      saveFailed: "Failed to save changes",
      uploadFailed: "Failed to upload photo",
      networkError: "Network connection error",
      tryAgain: "Please try again",
      authFailed: "Authentication failed",
      sessionExpired: "Session expired",
      invalidCredentials: "Invalid email or password",
      emailTaken: "Email is already in use",
      weakPassword: "Password is too weak",
      serverError: "Server error occurred",
      unauthorized: "Unauthorized access",
      forbidden: "Access forbidden",
      notFound: "Resource not found",
      tooManyRequests: "Too many requests",
      default: "Something went wrong"
    }
  },
  es: {
    form: {
      passwordStrong: "¡Contraseña fuerte!",
      passwordGettingThere: "Casi allí...",
      passwordMakeStronger: "Haz tu contraseña más fuerte",
      nameRequired: "El nombre es requerido",
      nameMinLength: "El nombre debe tener al menos 2 caracteres",
      error: "Error",
      errorOccurred: "Ha ocurrido un error"
    },
    welcome: {
      greeting: "¡Hola! Soy tu compañero de béisbol, ¡aquí para charlar sobre el juego que amamos! 💫⚾️",
      initialQuestion: "Cuéntame, ¿qué te hizo interesarte por el béisbol?",
      pageTitle: "Bienvenido a BallTales",
      pageSubtitle: "Hablemos de béisbol y conozcamos tus intereses",
      inputPlaceholder: "Escribe cualquier cosa sobre béisbol...",
      returnGreeting: "¡Bienvenido de nuevo a BallTales! ¿Listo para hablar más de béisbol? ⚾️"
    },
    auth: {
      welcomeBack: "Bienvenido de nuevo",
      welcomeNew: "Bienvenido",
      signInContinue: "Inicia sesión para continuar en BallTales",
      signUpJoin: "Regístrate para unirte a BallTales",
      email: "Correo electrónico",
      password: "Contraseña",
      name: "Tu nombre",
      rememberMe: "Recordarme",
      signIn: "Iniciar Sesión",
      signUp: "Registrarse",
      continue: "Continuar",
      createAccount: "Crear Cuenta",
      selectLanguage: "Seleccionar idioma",
      noAccount: "¿No tienes una cuenta?",
      haveAccount: "¿Ya tienes una cuenta?",
      forgotPassword: "¿Olvidaste tu contraseña?",
      accountCreated: "¡Cuenta creada exitosamente!",
      passwordReset: "Correo de restablecimiento enviado",
      sessionExpired: "Tu sesión ha expirado. Por favor, inicia sesión nuevamente.",
      verifyEmail: "Por favor, verifica tu dirección de correo",
      resendVerification: "Reenviar correo de verificación"
    },
    validation: {
      required: {
        email: "El correo electrónico es requerido",
        password: "La contraseña es requerida",
        name: "El nombre es requerido"
      },
      invalid: {
        email: "Por favor ingresa un correo electrónico válido",
        password: "La contraseña debe contener mayúsculas, minúsculas, números y caracteres especiales",
        name: "El nombre debe tener al menos 2 caracteres"
      },
      password: {
        tooShort: "Contraseña muy corta",
        makeStronger: "Haz tu contraseña más fuerte",
        gettingThere: "Casi allí...",
        strong: "¡Contraseña fuerte!",
        requirements: "Debe incluir: mayúsculas, minúsculas, números y caracteres especiales",
        minLength: "Mínimo 8 caracteres requeridos",
        match: "Las contraseñas deben coincidir"
      },
      name: {
        tooShort: "Nombre muy corto",
        minLength: "El nombre debe tener al menos 2 caracteres",
        maxLength: "El nombre no puede exceder 50 caracteres",
        invalid: "El nombre solo puede contener letras y espacios"
      }
    },
    profile: {
      baseballFan: "Aficionado al Béisbol",
      teamFanSuffix: "Aficionado",
      viewProfile: "Ver Perfil",
      editProfile: "Editar Perfil",
      uploadPhoto: "Subir Foto",
      analyzePhoto: "Analizar Foto"
    },
    statsSection: {
      title: "Estadísticas de Béisbol",
      messagesExchanged: "Mensajes Intercambiados",
      queriesAnswered: "Consultas Respondidas",
      daysActive: "Días Activos",
      gamesWatched: "Partidos Vistos",
      predictions: "Predicciones Realizadas",
      accuracy: "Precisión de Predicciones"
    },
    preferencesSection: {
      title: "Preferencias de Béisbol",
      favoriteTeam: "Equipo Favorito",
      favoritePlayer: "Jugador Favorito",
      memorableHomeRun: "Home Run Más Memorable",
      favoriteStadium: "Estadio Favorito",
      preferredPosition: "Posición Preferida",
      favoriteEra: "Era Favorita del Béisbol"
    },
    settings: {
      title: "Configuración",
      language: "Idioma",
      theme: "Tema",
      notifications: "Notificaciones",
      statsPreference: "Preferencia de Estadísticas",
      notificationPreference: "Preferencia de Notificaciones",
      privacySettings: "Configuración de Privacidad",
      dataPreferences: "Preferencias de Datos"
    },
    actions: {
      signOut: "Cerrar Sesión",
      save: "Guardar Cambios",
      cancel: "Cancelar",
      confirm: "Confirmar",
      edit: "Editar",
      delete: "Eliminar",
      view: "Ver Detalles"
    },
    notifications: {
      gameStart: "Partido Comenzando Pronto",
      scoreUpdate: "Actualización de Puntuación",
      playerStats: "Actualización de Estadísticas de Jugador",
      teamNews: "Noticias del Equipo",
      matchPrediction: "Predicción de Partido Disponible"
    },
    errors: {
      loadFailed: "Error al cargar el perfil",
      saveFailed: "Error al guardar cambios",
      uploadFailed: "Error al subir la foto",
      networkError: "Error de conexión de red",
      tryAgain: "Por favor, inténtalo de nuevo",
      authFailed: "Error de autenticación",
      sessionExpired: "Sesión expirada",
      invalidCredentials: "Correo o contraseña inválidos",
      emailTaken: "El correo ya está en uso",
      weakPassword: "La contraseña es demasiado débil",
      serverError: "Error del servidor",
      unauthorized: "Acceso no autorizado",
      forbidden: "Acceso prohibido",
      notFound: "Recurso no encontrado",
      tooManyRequests: "Demasiadas solicitudes",
      default: "Algo salió mal"
    }
  },
  ja: {
    form: {
      passwordStrong: "強いパスワードです！",
      passwordGettingThere: "もう少しです...",
      passwordMakeStronger: "より強いパスワードにしてください",
      nameRequired: "名前は必須です",
      nameMinLength: "名前は2文字以上必要です",
      error: "エラー",
      errorOccurred: "エラーが発生しました"
    },
    welcome: {
      greeting: "こんにちは！私はあなたの野球仲間です。大好きな野球について話しましょう！💫⚾️",
      initialQuestion: "野球を好きになったきっかけを教えてください。",
      pageTitle: "BallTalesへようこそ",
      pageSubtitle: "野球について話して、あなたの興味を教えてください",
      inputPlaceholder: "野球について何でも入力してください...",
      returnGreeting: "BallTalesへお帰りなさい！野球についてもっと話しましょう！⚾️"
    },
    auth: {
      welcomeBack: "おかえりなさい",
      welcomeNew: "ようこそ",
      signInContinue: "BallTalesを続けるにはサインインしてください",
      signUpJoin: "BallTalesに参加するには登録してください",
      email: "メールアドレス",
      password: "パスワード",
      name: "お名前",
      rememberMe: "ログイン情報を保存",
      signIn: "サインイン",
      signUp: "登録",
      continue: "続ける",
      createAccount: "アカウントを作成",
      selectLanguage: "言語を選択",
      noAccount: "アカウントをお持ちでない方",
      haveAccount: "すでにアカウントをお持ちの方",
      forgotPassword: "パスワードをお忘れの方",
      accountCreated: "アカウントが作成されました！",
      passwordReset: "パスワードリセットメールを送信しました",
      sessionExpired: "セッションが切れました。再度サインインしてください。",
      verifyEmail: "メールアドレスを確認してください",
      resendVerification: "確認メールを再送信"
    },
    validation: {
      required: {
        email: "メールアドレスは必須です",
        password: "パスワードは必須です",
        name: "名前は必須です"
      },
      invalid: {
        email: "有効なメールアドレスを入力してください",
        password: "パスワードは大文字、小文字、数字、特殊文字を含む必要があります",
        name: "名前は2文字以上である必要があります"
      },
      password: {
        tooShort: "パスワードが短すぎます",
        makeStronger: "より強いパスワードにしてください",
        gettingThere: "もう少しです...",
        strong: "強いパスワードです！",
        requirements: "必須：大文字、小文字、数字、特殊文字",
        minLength: "最低8文字必要です",
        match: "パスワードが一致しません"
      },
      name: {
        tooShort: "名前が短すぎます",
        minLength: "名前は2文字以上必要です",
        maxLength: "名前は50文字以内である必要があります",
        invalid: "名前には文字とスペースのみ使用できます"
      }
    },
    profile: {
      baseballFan: "野球ファン",
      teamFanSuffix: "ファン",
      viewProfile: "プロフィールを見る",
      editProfile: "プロフィールを編集",
      uploadPhoto: "写真をアップロード",
      analyzePhoto: "写真を分析"
    },
    statsSection: {
      title: "野球統計",
      messagesExchanged: "交換メッセージ",
      queriesAnswered: "回答済みクエリ",
      daysActive: "アクティブ日数",
      gamesWatched: "観戦した試合",
      predictions: "予測回数",
      accuracy: "予測精度"
    },
    preferencesSection: {
      title: "野球設定",
      favoriteTeam: "お気に入りチーム",
      favoritePlayer: "お気に入り選手",
      memorableHomeRun: "最も印象的なホームラン",
      favoriteStadium: "お気に入り球場",
      preferredPosition: "好きなポジション",
      favoriteEra: "好きな野球の時代"
    },
    settings: {
      title: "設定",
      language: "言語",
      theme: "テーマ",
      notifications: "通知",
      statsPreference: "統計設定",
      notificationPreference: "通知設定",
      privacySettings: "プライバシー設定",
      dataPreferences: "データ設定"
    },
    actions: {
      signOut: "サインアウト",
      save: "変更を保存",
      cancel: "キャンセル",
      confirm: "確認",
      edit: "編集",
      delete: "削除",
      view: "詳細を見る"
    },
    notifications: {
      gameStart: "まもなく試合開始",
      scoreUpdate: "スコア更新",
      playerStats: "選手統計更新",
      teamNews: "チームニュース",
      matchPrediction: "試合予測が利用可能"
    },
    errors: {
      loadFailed: "プロフィールの読み込みに失敗",
      saveFailed: "変更の保存に失敗",
      uploadFailed: "写真のアップロードに失敗",
      networkError: "ネットワーク接続エラー",
      tryAgain: "もう一度お試しください",
      authFailed: "認証エラー",
      sessionExpired: "セッションが切れました",
      invalidCredentials: "メールアドレスまたはパスワードが無効です",
      emailTaken: "このメールアドレスは既に使用されています",
      weakPassword: "パスワードが弱すぎます",
      serverError: "サーバーエラーが発生しました",
      unauthorized: "未認証のアクセス",
      forbidden: "アクセスが禁止されています",
      notFound: "リソースが見つかりません",
      tooManyRequests: "リクエストが多すぎます",
      default: "エラーが発生しました"
    }
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

export const NEXT_PUBLIC_API_URL = env('NEXT_PUBLIC_API_URL') ?? 'https://balltales-backend-527185366316.us-central1.run.app/api/v1';