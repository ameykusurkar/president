import React from "react";

export default function Card({ rank, suit, displayType }) {
  function colorClass() {
    return suit === 0 || suit === 2 ? "card-red" : "card-black";
  }

  function cardAsCodePoint() {
    if (rank === -1) {
      // Unicode for backface of a card
      return 0x1f0a0;
    }

    const suitOffset = codePointSuits[suit];
    // In President "3" is the lowest, so it has rank 0,
    // so add 2 to get it's rank in normal playing cards.
    var rankOffset = (rank + 2) % 13;
    if (rankOffset > 10) {
      // There's a weird "knight" card between Jack and Queen in the Unicode charset
      rankOffset++;
    }
    return suitOffset + rankOffset;
  }

  return (
    <div className={`card ${colorClass()} ${displayType}`}>
      {String.fromCodePoint(cardAsCodePoint())}
    </div>
  );
}

const codePointSuits = [
  0x1f0c1, // Ace of Diamonds
  0x1f0d1, // Ace of Clubs
  0x1f0b1, // Ace of Hearts
  0x1f0a1, // Ace of Spades
];
