"""Build test set from HotpotQA (preferred) or legacy hand-crafted extras."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOTPOT = Path(r"D:\HocAI\Day17\hotpot_dev_distractor_v1.json\hotpot_dev_distractor_v1.json")
OUT_PATH = ROOT / "data" / "my_test_set.json"


def build_from_hotpot(limit: int = 50, seed: int = 42) -> None:
    script = ROOT / "scripts" / "convert_hotpot.py"
    cmd = [sys.executable, str(script), "--limit", str(limit), "--seed", str(seed), "--output", str(OUT_PATH)]
    if DEFAULT_HOTPOT.exists():
        cmd.extend(["--input", str(DEFAULT_HOTPOT)])
    subprocess.run(cmd, check=True)


def build_legacy() -> None:
    import json

    MINI_PATH = ROOT / "data" / "hotpot_mini.json"
    EXTRA_QUESTIONS: list[dict] = [
    {"qid": "ex01", "difficulty": "easy", "question": "What genre is the novel written by the author of 1984?", "gold_answer": "dystopian fiction", "context": [{"title": "George Orwell", "text": "George Orwell wrote the dystopian novel 1984."}, {"title": "1984", "text": "1984 is a dystopian fiction novel."}]},
    {"qid": "ex02", "difficulty": "medium", "question": "Which sea borders the country where the Great Pyramid of Giza is located?", "gold_answer": "Mediterranean Sea", "context": [{"title": "Great Pyramid of Giza", "text": "The Great Pyramid of Giza is in Egypt."}, {"title": "Egypt", "text": "Egypt borders the Mediterranean Sea to the north."}]},
    {"qid": "ex03", "difficulty": "easy", "question": "What instrument is associated with the composer of Fur Elise?", "gold_answer": "piano", "context": [{"title": "Fur Elise", "text": "Fur Elise was composed by Ludwig van Beethoven."}, {"title": "Ludwig van Beethoven", "text": "Beethoven was a pianist and composer."}]},
    {"qid": "ex04", "difficulty": "medium", "question": "What is the official language of the country whose capital is Buenos Aires?", "gold_answer": "Spanish", "context": [{"title": "Buenos Aires", "text": "Buenos Aires is the capital of Argentina."}, {"title": "Argentina", "text": "The official language of Argentina is Spanish."}]},
    {"qid": "ex05", "difficulty": "easy", "question": "Which planet did the discoverer of Uranus also study as an astronomer?", "gold_answer": "Uranus", "context": [{"title": "William Herschel", "text": "William Herschel discovered the planet Uranus."}, {"title": "Uranus", "text": "Uranus is the seventh planet from the Sun."}]},
    {"qid": "ex06", "difficulty": "hard", "question": "Which mountain range is Mount Fuji part of in the country where Tokyo is the capital?", "gold_answer": "Japanese Alps", "context": [{"title": "Tokyo", "text": "Tokyo is the capital of Japan."}, {"title": "Mount Fuji", "text": "Mount Fuji in Japan is often grouped with the Japanese Alps region."}]},
    {"qid": "ex07", "difficulty": "medium", "question": "What river flows through the city that hosts the Colosseum?", "gold_answer": "Tiber", "context": [{"title": "Colosseum", "text": "The Colosseum is located in Rome."}, {"title": "Rome", "text": "Rome is situated on the Tiber river."}]},
    {"qid": "ex08", "difficulty": "easy", "question": "What nationality was the painter of The Starry Night?", "gold_answer": "Dutch", "context": [{"title": "The Starry Night", "text": "The Starry Night was painted by Vincent van Gogh."}, {"title": "Vincent van Gogh", "text": "Vincent van Gogh was a Dutch painter."}]},
    {"qid": "ex09", "difficulty": "medium", "question": "Which ocean is nearest to the country where Sydney Opera House is located?", "gold_answer": "Pacific Ocean", "context": [{"title": "Sydney Opera House", "text": "The Sydney Opera House is in Australia."}, {"title": "Australia", "text": "Australia is bordered by the Pacific Ocean to the east."}]},
    {"qid": "ex10", "difficulty": "easy", "question": "What field did Marie Curie win her first Nobel Prize in?", "gold_answer": "Physics", "context": [{"title": "Marie Curie", "text": "Marie Curie won the Nobel Prize in Physics in 1903."}, {"title": "Nobel Prize in Physics", "text": "The Nobel Prize in Physics honors discoveries in physics."}]},
    {"qid": "ex11", "difficulty": "medium", "question": "What is the currency of the country whose capital is Berlin?", "gold_answer": "euro", "context": [{"title": "Berlin", "text": "Berlin is the capital of Germany."}, {"title": "Germany", "text": "Germany uses the euro as its currency."}]},
    {"qid": "ex12", "difficulty": "easy", "question": "Who directed the movie that features the character Jack Dawson?", "gold_answer": "James Cameron", "context": [{"title": "Jack Dawson", "text": "Jack Dawson is a character in the film Titanic."}, {"title": "Titanic", "text": "Titanic was directed by James Cameron."}]},
    {"qid": "ex13", "difficulty": "hard", "question": "Which desert covers much of the country where Cairo is the capital?", "gold_answer": "Sahara", "context": [{"title": "Cairo", "text": "Cairo is the capital of Egypt."}, {"title": "Egypt", "text": "Much of Egypt is covered by the Sahara Desert."}]},
    {"qid": "ex14", "difficulty": "medium", "question": "What language is spoken in the country where the city of Montreal is located?", "gold_answer": "French", "context": [{"title": "Montreal", "text": "Montreal is a major city in Canada."}, {"title": "Canada", "text": "French is an official language of Canada and widely spoken in Montreal."}]},
    {"qid": "ex15", "difficulty": "easy", "question": "What sport is associated with the athlete who wore number 23 for the Chicago Bulls?", "gold_answer": "basketball", "context": [{"title": "Chicago Bulls", "text": "Michael Jordan wore number 23 for the Chicago Bulls."}, {"title": "Michael Jordan", "text": "Michael Jordan is a legendary basketball player."}]},
    {"qid": "ex16", "difficulty": "medium", "question": "Which continent is the country of Kenya located on?", "gold_answer": "Africa", "context": [{"title": "Kenya", "text": "Kenya is a country in East Africa."}, {"title": "Africa", "text": "Africa is the continent where Kenya is located."}]},
    {"qid": "ex17", "difficulty": "easy", "question": "What company did the founder of Microsoft establish?", "gold_answer": "Microsoft", "context": [{"title": "Bill Gates", "text": "Bill Gates co-founded Microsoft."}, {"title": "Microsoft", "text": "Microsoft is a technology company."}]},
    {"qid": "ex18", "difficulty": "hard", "question": "What is the tallest mountain in the country where Mount Kilimanjaro is located?", "gold_answer": "Mount Kilimanjaro", "context": [{"title": "Mount Kilimanjaro", "text": "Mount Kilimanjaro is in Tanzania."}, {"title": "Tanzania", "text": "Mount Kilimanjaro is the highest mountain in Tanzania."}]},
    {"qid": "ex19", "difficulty": "medium", "question": "Which strait separates the country where Madrid is the capital from Africa?", "gold_answer": "Strait of Gibraltar", "context": [{"title": "Madrid", "text": "Madrid is the capital of Spain."}, {"title": "Spain", "text": "Spain is separated from Africa by the Strait of Gibraltar."}]},
    {"qid": "ex20", "difficulty": "easy", "question": "What gas do plants produce during photosynthesis discovered by scientists studying chlorophyll?", "gold_answer": "oxygen", "context": [{"title": "Photosynthesis", "text": "Photosynthesis in plants produces oxygen."}, {"title": "Chlorophyll", "text": "Chlorophyll enables photosynthesis in plants."}]},
    {"qid": "ex21", "difficulty": "medium", "question": "What is the capital of the country where the Amazon River has its largest basin?", "gold_answer": "Brasilia", "context": [{"title": "Amazon River", "text": "The Amazon River has its largest basin in Brazil."}, {"title": "Brazil", "text": "The capital of Brazil is Brasilia."}]},
    {"qid": "ex22", "difficulty": "easy", "question": "Who wrote the play Hamlet performed by the Globe Theatre company?", "gold_answer": "William Shakespeare", "context": [{"title": "Globe Theatre", "text": "The Globe Theatre staged plays by William Shakespeare."}, {"title": "Hamlet", "text": "Hamlet was written by William Shakespeare."}]},
    {"qid": "ex23", "difficulty": "hard", "question": "Which plate boundary type is found near the country where Wellington is the capital?", "gold_answer": "subduction", "context": [{"title": "Wellington", "text": "Wellington is the capital of New Zealand."}, {"title": "New Zealand", "text": "New Zealand lies on a subduction plate boundary."}]},
    {"qid": "ex24", "difficulty": "medium", "question": "What religion is most common in the country where the city of Varanasi is located?", "gold_answer": "Hinduism", "context": [{"title": "Varanasi", "text": "Varanasi is a holy city in India."}, {"title": "India", "text": "Hinduism is the majority religion in India."}]},
    {"qid": "ex25", "difficulty": "easy", "question": "What element has the chemical symbol associated with the lightest noble gas?", "gold_answer": "helium", "context": [{"title": "Noble gases", "text": "Helium is the lightest noble gas."}, {"title": "Helium", "text": "Helium has the chemical symbol He."}]},
    {"qid": "ex26", "difficulty": "medium", "question": "Which country invented the sport associated with the Wimbledon tournament?", "gold_answer": "England", "context": [{"title": "Wimbledon", "text": "Wimbledon is a tennis tournament held in England."}, {"title": "Tennis", "text": "Modern lawn tennis originated in England."}]},
    {"qid": "ex27", "difficulty": "easy", "question": "What is the pen name of the author who wrote The Adventures of Tom Sawyer?", "gold_answer": "Mark Twain", "context": [{"title": "The Adventures of Tom Sawyer", "text": "The Adventures of Tom Sawyer was written by Mark Twain."}, {"title": "Mark Twain", "text": "Mark Twain was the pen name of Samuel Clemens."}]},
    {"qid": "ex28", "difficulty": "hard", "question": "What is the deepest lake in the country where Lake Baikal is located?", "gold_answer": "Lake Baikal", "context": [{"title": "Lake Baikal", "text": "Lake Baikal is located in Russia."}, {"title": "Russia", "text": "Lake Baikal is the deepest lake in Russia."}]},
    {"qid": "ex29", "difficulty": "medium", "question": "What sea lies east of the country where Athens is the capital?", "gold_answer": "Aegean Sea", "context": [{"title": "Athens", "text": "Athens is the capital of Greece."}, {"title": "Greece", "text": "The Aegean Sea lies to the east of Greece."}]},
    {"qid": "ex30", "difficulty": "easy", "question": "What theory is Albert Einstein best known for besides relativity?", "gold_answer": "photoelectric effect", "context": [{"title": "Albert Einstein", "text": "Einstein explained the photoelectric effect and won a Nobel Prize for it."}, {"title": "Photoelectric effect", "text": "The photoelectric effect is a quantum phenomenon."}]},
    {"qid": "ex31", "difficulty": "medium", "question": "What is the largest city in the country where the Danube River ends its course?", "gold_answer": "Belgrade", "context": [{"title": "Danube River", "text": "The Danube River flows through Serbia before reaching the Black Sea."}, {"title": "Serbia", "text": "Belgrade is the largest city in Serbia."}]},
    {"qid": "ex32", "difficulty": "easy", "question": "Who painted the ceiling of the building where papal conclaves are held in Vatican City?", "gold_answer": "Michelangelo", "context": [{"title": "Sistine Chapel", "text": "The Sistine Chapel ceiling was painted by Michelangelo."}, {"title": "Vatican City", "text": "The Sistine Chapel is in Vatican City where papal conclaves are held."}]},
    {"qid": "ex33", "difficulty": "hard", "question": "What climate zone covers most of the country where the Outback is found?", "gold_answer": "arid", "context": [{"title": "Outback", "text": "The Outback is a remote arid region of Australia."}, {"title": "Australia", "text": "Much of Australia has an arid climate."}]},
    {"qid": "ex34", "difficulty": "medium", "question": "What is the official language of the country where Seoul is the capital?", "gold_answer": "Korean", "context": [{"title": "Seoul", "text": "Seoul is the capital of South Korea."}, {"title": "South Korea", "text": "The official language of South Korea is Korean."}]},
    {"qid": "ex35", "difficulty": "easy", "question": "What organ pumps blood in the body studied by cardiologists?", "gold_answer": "heart", "context": [{"title": "Cardiology", "text": "Cardiologists study the heart and cardiovascular system."}, {"title": "Heart", "text": "The heart pumps blood throughout the body."}]},
    {"qid": "ex36", "difficulty": "medium", "question": "Which country borders both the country where Warsaw is the capital and Germany?", "gold_answer": "Poland", "context": [{"title": "Warsaw", "text": "Warsaw is the capital of Poland."}, {"title": "Poland", "text": "Poland shares a border with Germany."}]},
    {"qid": "ex37", "difficulty": "easy", "question": "What is the chemical formula for the compound commonly known as table salt?", "gold_answer": "NaCl", "context": [{"title": "Table salt", "text": "Table salt is sodium chloride."}, {"title": "Sodium chloride", "text": "Sodium chloride has the chemical formula NaCl."}]},
    {"qid": "ex38", "difficulty": "hard", "question": "What is the highest waterfall in the country where Angel Falls is located?", "gold_answer": "Angel Falls", "context": [{"title": "Angel Falls", "text": "Angel Falls is located in Venezuela."}, {"title": "Venezuela", "text": "Angel Falls is the highest waterfall in Venezuela."}]},
    {"qid": "ex39", "difficulty": "medium", "question": "What body of water lies between the country where Stockholm is the capital and Finland?", "gold_answer": "Baltic Sea", "context": [{"title": "Stockholm", "text": "Stockholm is the capital of Sweden."}, {"title": "Sweden", "text": "Sweden lies on the Baltic Sea across from Finland."}]},
    {"qid": "ex40", "difficulty": "easy", "question": "Who developed the polio vaccine used widely in the 1950s?", "gold_answer": "Jonas Salk", "context": [{"title": "Polio vaccine", "text": "The inactivated polio vaccine was developed by Jonas Salk."}, {"title": "Jonas Salk", "text": "Jonas Salk introduced his polio vaccine in the 1950s."}]},
    {"qid": "ex41", "difficulty": "medium", "question": "What is the main export crop of the country where Bogota is the capital?", "gold_answer": "coffee", "context": [{"title": "Bogota", "text": "Bogota is the capital of Colombia."}, {"title": "Colombia", "text": "Colombia is a major exporter of coffee."}]},
    {"qid": "ex42", "difficulty": "easy", "question": "What planet is known as the Red Planet studied by NASA rovers?", "gold_answer": "Mars", "context": [{"title": "NASA rovers", "text": "NASA has sent rovers to Mars."}, {"title": "Mars", "text": "Mars is known as the Red Planet."}]},
]


    import json

    MINI_PATH = ROOT / "data" / "hotpot_mini.json"
    mini = json.loads(MINI_PATH.read_text(encoding="utf-8"))
    combined = mini + EXTRA_QUESTIONS
    if len(combined) < 50:
        raise SystemExit(f"Need at least 50 examples, got {len(combined)}")
    OUT_PATH.write_text(json.dumps(combined, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(combined)} legacy examples to {OUT_PATH}")


def main() -> None:
    if DEFAULT_HOTPOT.exists():
        build_from_hotpot(limit=50, seed=42)
    else:
        print(f"Hotpot file not found at {DEFAULT_HOTPOT}, using legacy hand-crafted set.")
        build_legacy()


if __name__ == "__main__":
    main()
