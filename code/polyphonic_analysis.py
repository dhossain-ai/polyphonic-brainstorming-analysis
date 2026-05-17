"""
Polyphonic Brainstorming Analysis

This script analyzes brainstorming chat logs using a simple keyword-based
polyphonic analysis approach.

It detects:
1. Voices: repeated perspectives in the dialogue
2. Convergences: when two voices appear together in the same utterance
3. Divergences: when voices appear with contrast/disagreement markers

Input:
    chat_logs/*.txt

Output:
    results/results_<original_filename>.txt
"""

from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations


CHAT_LOG_DIR = Path("chat_logs")
RESULTS_DIR = Path("results")


VOICE_KEYWORDS = {
    "Technical voice": [
        "machine", "ai", "algorithm", "data", "model", "training",
        "generate", "output", "patterns", "statistical", "code",
        "system", "tool", "recombine", "recombining"
    ],
    "Human-centered voice": [
        "human", "humans", "feeling", "feelings", "emotion", "emotions",
        "intention", "intentions", "consciousness", "conscious",
        "understand", "understanding", "experience", "experiences",
        "meaning", "awareness", "motivation", "personal"
    ],
    "Social voice": [
        "people", "audience", "society", "social", "judge", "judged",
        "recognize", "recognized", "valuable", "value", "culture",
        "creative value", "find it creative"
    ],
    "Ethical/legal voice": [
        "ethical", "ethics", "credit", "ownership", "responsibility",
        "responsible", "plagiarism", "copyright", "bias", "artists",
        "developers", "training data"
    ],
}


DIVERGENCE_MARKERS = [
    "but", "however", "although", "though", "disagree",
    "not sure", "not fully convinced", "on the other hand",
    "different from", "not the same", "instead"
]


def read_chat_log(file_path):
    """Read a chat log file and return its lines."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()


def extract_utterances(lines):
    """
    Extract utterances from the chat log.

    An utterance is a line that contains a speaker label, for example:
    StudentA: I think a machine can be creative.
    """
    utterances = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if ":" not in line:
            continue

        speaker, text = line.split(":", 1)
        speaker = speaker.strip()
        text = text.strip()

        # Ignore metadata lines such as Session, Type, Topic, Participants
        if speaker.lower() in ["session", "type", "topic", "participants"]:
            continue

        if text:
            utterances.append({
                "speaker": speaker,
                "text": text
            })

    return utterances


def detect_voices(text):
    """
    Detect voices in one utterance using keyword matching.

    Returns a list of voice names found in the utterance.
    """
    text_lower = text.lower()
    detected = []

    for voice, keywords in VOICE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected.append(voice)
                break

    return detected


def has_divergence_marker(text):
    """Check whether the utterance contains a contrast/disagreement marker."""
    text_lower = text.lower()

    for marker in DIVERGENCE_MARKERS:
        if marker in text_lower:
            return True

    return False


def analyze_chat_log(file_path):
    """Analyze one chat log and return a text report."""
    lines = read_chat_log(file_path)
    utterances = extract_utterances(lines)

    voice_counts = Counter()
    convergence_counts = Counter()
    divergence_counts = Counter()
    speaker_counts = Counter()

    analyzed_utterances = []

    for utterance in utterances:
        speaker = utterance["speaker"]
        text = utterance["text"]

        voices = detect_voices(text)
        divergence_marker = has_divergence_marker(text)

        speaker_counts[speaker] += 1

        for voice in voices:
            voice_counts[voice] += 1

        if len(voices) >= 2:
            for pair in combinations(sorted(voices), 2):
                convergence_counts[pair] += 1

                if divergence_marker:
                    divergence_counts[pair] += 1

        analyzed_utterances.append({
            "speaker": speaker,
            "text": text,
            "voices": voices,
            "divergence_marker": divergence_marker
        })

    report = create_report(
        file_path=file_path,
        utterances=utterances,
        analyzed_utterances=analyzed_utterances,
        speaker_counts=speaker_counts,
        voice_counts=voice_counts,
        convergence_counts=convergence_counts,
        divergence_counts=divergence_counts
    )

    return report


def create_report(
    file_path,
    utterances,
    analyzed_utterances,
    speaker_counts,
    voice_counts,
    convergence_counts,
    divergence_counts
):
    """Create a readable analysis report."""
    lines = []

    lines.append("POLYPHONIC ANALYSIS REPORT")
    lines.append("=" * 40)
    lines.append(f"File analyzed: {file_path.name}")
    lines.append(f"Total utterances: {len(utterances)}")
    lines.append("")

    lines.append("SPEAKER TURN COUNTS")
    lines.append("-" * 40)
    for speaker, count in speaker_counts.items():
        lines.append(f"- {speaker}: {count} turns")
    lines.append("")

    lines.append("DETECTED VOICES")
    lines.append("-" * 40)
    if voice_counts:
        for voice, count in voice_counts.most_common():
            lines.append(f"- {voice}: {count} utterances")
    else:
        lines.append("- No voices detected")
    lines.append("")

    lines.append("CONVERGENCES")
    lines.append("-" * 40)
    if convergence_counts:
        for (voice_one, voice_two), count in convergence_counts.most_common():
            lines.append(f"- {voice_one} + {voice_two}: {count} times")
    else:
        lines.append("- No convergences detected")
    lines.append("")

    lines.append("DIVERGENCES")
    lines.append("-" * 40)
    if divergence_counts:
        for (voice_one, voice_two), count in divergence_counts.most_common():
            lines.append(f"- {voice_one} vs {voice_two}: {count} contrast markers")
    else:
        lines.append("- No divergences detected")
    lines.append("")

    lines.append("UTTERANCE-LEVEL ANALYSIS")
    lines.append("-" * 40)

    for index, item in enumerate(analyzed_utterances, start=1):
        voices_text = ", ".join(item["voices"]) if item["voices"] else "No voice detected"
        divergence_text = "Yes" if item["divergence_marker"] else "No"

        lines.append(f"{index}. {item['speaker']}: {item['text']}")
        lines.append(f"   Voices: {voices_text}")
        lines.append(f"   Divergence marker: {divergence_text}")

    return "\n".join(lines)


def save_report(input_file, report):
    """Save the analysis report to the results folder."""
    RESULTS_DIR.mkdir(exist_ok=True)

    output_name = f"results_{input_file.stem}.txt"
    output_path = RESULTS_DIR / output_name

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(report)

    return output_path


def main():
    """Analyze all .txt files in the chat_logs folder."""
    chat_files = sorted(CHAT_LOG_DIR.glob("*.txt"))

    if not chat_files:
        print("No chat log files found in the chat_logs folder.")
        return

    for chat_file in chat_files:
        report = analyze_chat_log(chat_file)
        output_path = save_report(chat_file, report)
        print(f"Analyzed {chat_file.name} -> {output_path}")


if __name__ == "__main__":
    main()