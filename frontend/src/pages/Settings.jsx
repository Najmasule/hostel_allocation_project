import { useState } from "react";
import { useLanguage } from "../language";

export default function Settings() {
  const { language, setLanguage, t } = useLanguage();
  const [saved, setSaved] = useState(false);

  function onLanguageChange(e) {
    setLanguage(e.target.value);
    setSaved(true);
  }

  return (
    <section className="section">
      <h2>{t("settings")}</h2>
      <p className="subtitle">{t("chooseLanguage")}</p>
      {saved && <p className="success">{t("languageSaved")}</p>}
      <form className="form-grid">
        <label htmlFor="language">{t("language")}</label>
        <select id="language" value={language} onChange={onLanguageChange}>
          <option value="en">{t("english")}</option>
          <option value="sw">{t("swahili")}</option>
        </select>
      </form>
    </section>
  );
}
