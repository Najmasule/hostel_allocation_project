import { createContext, createElement, useContext, useEffect, useMemo, useState } from "react";

const translations = {
  en: {
    settings: "Settings",
    language: "Language",
    languageSaved: "Language updated successfully.",
    english: "English",
    swahili: "Swahili",
    chooseLanguage: "Choose your preferred system language.",
    allocationStatus: "Your Allocation Status",
    pendingStatus: "Your application is pending or you have not applied yet.",
    allocatedTo: "You have been allocated to",
    room: "Room",
    notAssigned: "Not assigned yet",
    allocatedOn: "Allocated on",
    home: "Home",
    viewHostel: "View Hostel",
    applyHostel: "Apply for Hostel",
    status: "Allocation Status",
  },
  sw: {
    settings: "Mipangilio",
    language: "Lugha",
    languageSaved: "Lugha imebadilishwa kwa mafanikio.",
    english: "Kiingereza",
    swahili: "Kiswahili",
    chooseLanguage: "Chagua lugha unayotaka kutumia kwenye mfumo.",
    allocationStatus: "Hali ya Ugawaji",
    pendingStatus: "Maombi yako yanasubiri au bado hujaomba hostel.",
    allocatedTo: "Umegawiwa",
    room: "Chumba",
    notAssigned: "Bado hakijatolewa",
    allocatedOn: "Tarehe ya Ugawaji",
    home: "Mwanzo",
    viewHostel: "Ona Hostel",
    applyHostel: "Omba Hostel",
    status: "Hali ya Ugawaji",
  },
};

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => localStorage.getItem("app_language") || "en");

  useEffect(() => {
    localStorage.setItem("app_language", language);
  }, [language]);

  const value = useMemo(
    () => ({
      language,
      setLanguage,
      t: (key) => translations[language]?.[key] || translations.en[key] || key,
    }),
    [language]
  );

  return createElement(LanguageContext.Provider, { value }, children);
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    return {
      language: "en",
      setLanguage: () => {},
      t: (key) => translations.en[key] || key,
    };
  }
  return context;
}
