// Funkcja zamieniająca string (np. nazwę miasta) na stałą liczbę całkowitą
const getHash = (str) => str.split('').reduce((a, b) => (((a << 5) - a) + b.charCodeAt(0)) | 0, 0);

// Funkcja wybierająca element z tablicy na podstawie stałego seeda
const pick = (arr, seed) => arr[Math.abs(seed) % arr.length];

export function getCostAnswer(city, minCost, maxCost) {
  const seed = getHash(city + "cost");
  const intros = [
    `Based on current labor modifiers and geological data, the estimated cost for foundation stabilization in ${city}`,
    `Homeowners in the ${city} area can expect base repair investments`,
    `When calculating expenses for a standard 1,500 sq ft footprint in ${city}, local structural estimates`,
    `According to our aggregated municipal data, foundation correction pricing in ${city}`
  ];
  const outros = [
    `typically ranges between $${minCost} and $${maxCost}.`,
    `usually falls within the $${minCost} - $${maxCost} spectrum.`,
    `is currently evaluated between $${minCost} and $${maxCost}.`,
    `will run from $${minCost} up to $${maxCost} depending on pier depth requirements.`
  ];
  return `${pick(intros, seed)} ${pick(outros, seed)}`;
}

export function getCauseAnswer(city, soilIndex, droughtStatus) {
  const seed = getHash(city + "cause");
  const isHighRisk = soilIndex >= 70;
  
  const soilPhrases = isHighRisk 
    ? [
        `the severe shrink-swell potential of the local expansive clay (USDA Index: ${soilIndex})`,
        `highly volatile soil compositions specific to this zone (USDA Index: ${soilIndex})`,
        `aggressive subterranean shifting caused by high-plasticity clay (USDA Index: ${soilIndex})`
      ]
    : [
        `moderate settling associated with local loam and clay mixtures (USDA Index: ${soilIndex})`,
        `gradual soil compaction over time (USDA Index: ${soilIndex})`,
        `standard geological shifting observed in this region (USDA Index: ${soilIndex})`
      ];
      
  const droughtPhrases = [
    `Combined with the current ${droughtStatus.toLowerCase()} drought conditions, this causes severe ground movement.`,
    `The situation is further accelerated by ongoing ${droughtStatus.toLowerCase()} drought patterns in the region.`,
    `When exposed to ${droughtStatus.toLowerCase()} drought cycles, the loss of hydrostatic pressure destabilizes the concrete slab.`
  ];

  const intros = [
    `A primary cause of foundation failure in ${city} is`,
    `Structural engineers frequently trace foundation issues in ${city} back to`,
    `The leading geological culprit for slab deterioration in ${city} remains`
  ];

  return `${pick(intros, seed)} ${pick(soilPhrases, seed)}. ${pick(droughtPhrases, seed)}`;
}

export function getInspectionAnswer(city) {
  const seed = getHash(city + "inspection");
  const answers = [
    `Yes, property owners in the ${city} area can receive a free initial clinical estimate by calling the displayed toll-free dispatch number.`,
    `Absolutely. We route ${city} residents to local service providers who provide zero-cost, no-obligation physical assessments of the structural damage.`,
    `Initial evaluations are complimentary. By contacting the 24/7 dispatch, ${city} homeowners can secure a free site visit from a local repair contractor.`
  ];
  return pick(answers, seed);
}
