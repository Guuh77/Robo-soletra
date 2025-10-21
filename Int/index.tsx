/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

// Elementos do DOM
const startBotButton = document.getElementById('start-bot-button') as HTMLButtonElement;
const instructionsContainer = document.getElementById('instructions-container') as HTMLDivElement;

// Adiciona um listener ao botão principal
startBotButton.addEventListener('click', showInstructions);

/**
 * Exibe a seção de instruções e rola a página para visualizá-la.
 */
function showInstructions() {
  // Se as instruções já estiverem visíveis, não faz nada.
  if (instructionsContainer.style.display === 'block') {
    return;
  }

  instructionsContainer.style.display = 'block';
  instructionsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
