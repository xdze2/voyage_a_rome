export const skills = [
  { id: 1,  label: "Concevoir des interfaces que les gens trouvent jolies" },
  { id: 2,  label: "Animer des réunions qui finissent à l'heure" },
  { id: 3,  label: "Écrire du code qui fonctionne le vendredi soir" },
  { id: 4,  label: "Convaincre un client que son idée mérite d'évoluer" },
  { id: 5,  label: "Lire une documentation technique de 200 pages" },
  { id: 6,  label: "Désamorcer des conflits entre collègues" },
  { id: 7,  label: "Travailler seul sans perdre le fil" },
  { id: 8,  label: "Expliquer des trucs compliqués à des gens pressés" },
  { id: 9,  label: "Analyser des données et en tirer quelque chose d'utile" },
  { id: 10, label: "Créer des visuels qui racontent une histoire" },
  { id: 11, label: "Jongler avec plusieurs projets en même temps" },
  { id: 12, label: "Transformer une idée vague en quelque chose de livrable" },
]

export const jobs = [
  {
    id: "DEV",
    label: "Développeur·euse web",
    url: "https://candidat.francetravail.fr/metierscope/#/fiche-metier/M1805",
    skills: [3, 5, 7, 9, 12],
  },
  {
    id: "CHEF",
    label: "Chef·fe de projet",
    url: "https://candidat.francetravail.fr/metierscope/#/fiche-metier/M1403",
    skills: [2, 4, 6, 8, 11],
  },
  {
    id: "UX",
    label: "Designer UX/UI",
    url: "https://candidat.francetravail.fr/metierscope/#/fiche-metier/E1205",
    skills: [1, 10, 12, 8, 4],
  },
  {
    id: "DATA",
    label: "Data Analyst",
    url: "https://candidat.francetravail.fr/metierscope/#/fiche-metier/M1805",
    skills: [5, 9, 7, 3, 8],
  },
  {
    id: "COM",
    label: "Chargé·e de communication",
    url: "https://candidat.francetravail.fr/metierscope/#/fiche-metier/E1103",
    skills: [4, 8, 10, 11, 6],
  },
  {
    id: "CONSULT",
    label: "Consultant·e",
    url: "https://candidat.francetravail.fr/metierscope/#/fiche-metier/M1403",
    skills: [4, 8, 11, 12, 2],
  },
  {
    id: "DA",
    label: "Directeur·rice artistique",
    url: "https://candidat.francetravail.fr/metierscope/#/fiche-metier/E1205",
    skills: [1, 10, 4, 12, 2],
  },
  {
    id: "PM",
    label: "Product Manager",
    url: "https://candidat.francetravail.fr/metierscope/#/fiche-metier/M1403",
    skills: [2, 4, 8, 11, 12],
  },
]

/** Generate a shuffled list of unique pairs */
export function generatePairs(count = 15) {
  const ids = skills.map(s => s.id)
  const all = []
  for (let i = 0; i < ids.length; i++)
    for (let j = i + 1; j < ids.length; j++)
      all.push([ids[i], ids[j]])

  // Fisher-Yates shuffle
  for (let i = all.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [all[i], all[j]] = [all[j], all[i]]
  }
  return all.slice(0, Math.min(count, all.length))
}
