// src/utils/urlFetcher.ts

const CORS_PROXY = "https://cors-anywhere.herokuapp.com/";
const SCRAPER_API = "https://api.scraperapi.com";

interface FetchUrlResult {
  success: boolean;
  content?: string;
  error?: string;
}

/**
 * Extracts text content from a URL using multiple methods
 */
export const fetchUrlContent = async (
  url: string
): Promise<FetchUrlResult> => {
  // Validate URL
  if (!isValidUrl(url)) {
    return {
      success: false,
      error: "Invalid URL format. Please enter a valid web address.",
    };
  }

  // Try different methods
  try {
    // Method 1: Direct fetch with CORS
    const directResult = await tryDirectFetch(url);
    if (directResult.success) return directResult;

    // Method 2: CORS Proxy
    const proxyResult = await tryCorsproxy(url);
    if (proxyResult.success) return proxyResult;

    // If all methods fail
    return {
      success: false,
      error: "Could not fetch URL. Please paste the content manually.",
    };
  } catch (error) {
    return {
      success: false,
      error: `Error fetching URL: ${
        error instanceof Error ? error.message : "Unknown error"
      }`,
    };
  }
};

/**
 * Try direct fetch without proxy
 */
const tryDirectFetch = async (url: string): Promise<FetchUrlResult> => {
  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      },
    });

    if (!response.ok) {
      return { success: false };
    }

    const html = await response.text();
    const content = extractTextFromHtml(html);

    if (content.trim().length > 50) {
      return { success: true, content };
    }

    return { success: false };
  } catch {
    return { success: false };
  }
};

/**
 * Try using CORS proxy
 */
const tryCorsproxy = async (url: string): Promise<FetchUrlResult> => {
  try {
    const response = await fetch(`${CORS_PROXY}${url}`, {
      method: "GET",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    if (!response.ok) {
      return { success: false };
    }

    const html = await response.text();
    const content = extractTextFromHtml(html);

    if (content.trim().length > 50) {
      return { success: true, content };
    }

    return { success: false };
  } catch {
    return { success: false };
  }
};

/**
 * Extract readable text from HTML
 */
const extractTextFromHtml = (html: string): string => {
  // Remove script and style tags
  let text = html
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
    .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, "");

  // Remove HTML tags
  text = text.replace(/<[^>]+>/g, " ");

  // Decode HTML entities
  text = decodeHtmlEntities(text);

  // Clean up whitespace
  text = text
    .replace(/\s+/g, " ") // Multiple spaces to single space
    .replace(/\n\s*\n/g, "\n") // Multiple newlines to single
    .trim();

  return text;
};

/**
 * Decode HTML entities
 */
const decodeHtmlEntities = (text: string): string => {
  const textarea = document.createElement("textarea");
  textarea.innerHTML = text;
  return textarea.value;
};

/**
 * Validate URL format
 */
const isValidUrl = (url: string): boolean => {
  try {
    new URL(url.startsWith("http") ? url : `https://${url}`);
    return true;
  } catch {
    return false;
  }
};

/**
 * Check if URL is a YouTube link and extract transcript
 */
export const isYouTubeUrl = (url: string): boolean => {
  return (
    url.includes("youtube.com") ||
    url.includes("youtu.be") ||
    url.includes("youtube")
  );
};

/**
 * Get video ID from YouTube URL
 */
const getYouTubeVideoId = (url: string): string | null => {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/,
    /youtube\.com\/embed\/([^&\n?#]+)/,
  ];

  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match && match[1]) return match[1];
  }

  return null;
};

/**
 * Fetch YouTube transcript (requires backend or API)
 */
export const fetchYouTubeTranscript = async (
  url: string
): Promise<FetchUrlResult> => {
  const videoId = getYouTubeVideoId(url);

  if (!videoId) {
    return {
      success: false,
      error: "Could not extract video ID from YouTube URL.",
    };
  }

  // Note: This requires a backend service or API
  // For now, we'll return a message guiding the user
  return {
    success: false,
    error: `YouTube URL detected. Please extract the transcript manually:
1. Go to the video
2. Click the three dots (⋯) below the video
3. Select "Show transcript"
4. Copy the transcript text
5. Paste it here

Or visit: https://www.yt-script.com/ and paste this URL to auto-extract.`,
  };
};