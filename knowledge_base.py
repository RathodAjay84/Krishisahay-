"""Small India-focused retrieval layer for grounded farming answers."""

from __future__ import annotations

KNOWLEDGE = [
    (('yellow', 'pale', 'nitrogen', 'deficiency'), 'Yellowing can come from nitrogen deficiency, waterlogging, drought stress, root damage, or disease. Older leaves turning uniformly pale often suggest a nutrient or root-zone issue, while spots, curling, or uneven patches need closer inspection. Do not apply urea only from leaf colour; check crop stage, soil moisture, and a soil test first.'),
    (('cotton', 'bollworm', 'boll', 'square'), 'For cotton, inspect squares and bolls for entry holes, frass, shed flowers, and larval damage. Pheromone traps and field sanitation can support integrated pest management. Confirm the pest before spraying and follow the registered product label and local agriculture guidance.'),
    (('chilli', 'chili', 'thrips', 'leaf curl'), 'In chilli, inspect new leaves and flowers for thrips, silvering, curling, and scarring. Blue sticky traps and field sanitation can help. Leaf curl has multiple possible causes, so check for whiteflies and other insects before selecting treatment.'),
    (('paddy', 'rice', 'stem borer', 'tiller'), 'In paddy, inspect tillers for dead hearts or white ears and check leaves and stems before treatment. Avoid continuous deep standing water when the crop does not need it. Confirm stem borer or another cause before using a pesticide.'),
    (('soil', 'moisture', 'irrigation', 'water'), 'Check moisture at root depth rather than only looking at the soil surface. Irrigate during cooler hours when needed, avoid waterlogging, repair leaks, and use mulch where practical. Crop stage, soil type, rainfall, and sensor readings should guide irrigation timing.'),
    (('fertilizer', 'urea', 'npk', 'ph'), 'Fertilizer decisions should use the crop, growth stage, soil test, and realistic yield goal. Split nitrogen applications, avoid urea just before heavy rain, and do not mix products unless the label permits it.'),
]

RESOURCES = (
    'ICAR: https://icar.gov.in/',
    'Kisan Call Centre: https://mkisan.gov.in/',
    'PPQS: https://ppqs.gov.in/',
    'Soil Health Card: https://soilhealth.dac.gov.in/',
    'IMD: https://mausam.imd.gov.in/',
    'Agmarknet: https://agmarknet.gov.in/',
)


def retrieve_context(query: str) -> str:
    query_lower = query.lower()
    matches = []
    for topics, text in KNOWLEDGE:
        score = sum(topic in query_lower for topic in topics)
        if score:
            matches.append((score, text))
    matches.sort(reverse=True)
    selected = [text for _, text in matches[:3]]
    if not selected:
        selected = ['No crop-specific note matched. Ask for crop, location, season, symptoms, and sensor readings before diagnosing.']
    return 'Retrieved local guidance:\n- ' + '\n- '.join(selected) + '\n\nTrusted resources:\n- ' + '\n- '.join(RESOURCES)
