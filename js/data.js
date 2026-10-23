// Default Mock Data
const INITIAL_DEMON_LIST = [
  { id: 1, rank: 1, name: "Acheron", creator: "Riot & More", verifier: "Zoink", levelId: "84347710", difficulty: "Top 1 Demon", points: 250, video: "https://www.youtube.com/embed/dQw4w9WgXcQ", isSpecial: true },
  { id: 2, rank: 2, name: "Avernus", creator: "Pringles & More", verifier: "Diamond", levelId: "91238472", difficulty: "Top 2 Demon", points: 230, video: "https://www.youtube.com/embed/dQw4w9WgXcQ", isSpecial: false },
  { id: 3, rank: 3, name: "Silent Clubstep", creator: "Nailokis", verifier: "Paqtez", levelId: "82019483", difficulty: "Top 3 Demon", points: 210, video: "https://www.youtube.com/embed/dQw4w9WgXcQ", isSpecial: true },
  { id: 4, rank: 4, name: "Slaughterhouse", creator: "IcedCave", verifier: "Spaceuk", levelId: "73928104", difficulty: "Top 4 Demon", points: 190, video: "https://www.youtube.com/embed/dQw4w9WgXcQ", isSpecial: false },
];

const INITIAL_COLLABS = [
  {
    id: 1,
    title: "FIH Megacollab #1 - Cybernetics",
    host: "PlayerLBM",
    description: "Looking for top-tier layout creators and decorators for extreme demon project.",
    slotsNeeded: 8,
    slotsFilled: 5,
    difficulty: "Extreme Demon",
    deadline: "2026-12-31",
    applicants: [
      { username: "GD_Master", status: "Accepted" },
      { username: "VortexCreator", status: "Pending" }
    ]
  },
  {
    id: 2,
    title: "FIH Mini Collab - Sunset Breeze",
    host: "AquaDash",
    description: "Chilled glow style level collab.",
    slotsNeeded: 4,
    slotsFilled: 2,
    difficulty: "Insane Demon",
    deadline: "2026-10-15",
    applicants: []
  }
];

const INITIAL_USER = {
  username: "Player LBM",
  pfp: "https://via.placeholder.com/80",
  achievement: "FIH Verification Specialist",
  points: 1450,
  maxPoints: 2000
};

const INITIAL_HELPERS = [
  { id: 1, name: "VortXX", role: "Playtester / Verifier", contact: "VortXX#1234", status: "Available" },
  { id: 2, name: "GlowArt", role: "Decorator (Glow Style)", contact: "GlowArt#5678", status: "Busy" }
];
