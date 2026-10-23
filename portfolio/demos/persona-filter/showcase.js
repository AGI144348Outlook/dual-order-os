// Synthetic demonstration using the preserved upstream filter, not a new model.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {deriveConversation} from './vendor/experiments/session-towers/engine.js';

const turns = [
  ['user', 'We should discuss Julian tomorrow.'],
  ['assistant', 'Noted.'],
  ['user', 'Julian, help outline a garden story.'],
  ['assistant', 'Let us begin with the gardener.'],
  ['user', 'Continue with the setting.'],
  ['assistant', 'The garden surrounds an abandoned observatory.'],
  ['user', 'Nexus, take over this separate task.'],
  ['assistant', 'I will organize the inventory.'],
];
const mapping = {};
turns.forEach(([role, text], index) => {
  const id = 'n' + index;
  mapping[id] = {
    parent: index ? 'n' + (index - 1) : null,
    children: index + 1 < turns.length ? ['n' + (index + 1)] : [],
    message: {
      id, author: {role}, create_time: 1000 + index,
      content: {content_type: 'text', parts: [text]},
    },
  };
});
const conversation = {id: 'synthetic-demo', current_node: 'n7', mapping};
const result = deriveConversation(conversation, {
  fileId: 'synthetic-demo',
  sha256: createHash('sha256').update(JSON.stringify(conversation)).digest('hex'),
  conversationId: conversation.id,
});
assert.equal(result.error, null);
assert.deepEqual(result.julian.map(row => row.tier), ['direct', 'inherited']);
assert.deepEqual(result.julian.map(row => row.reply.nodeId), ['n3', 'n5']);
console.log(JSON.stringify({
  synthetic_data: true,
  model_calls: 0,
  input_messages: turns.length,
  candidate_pairs: result.julian.map(row => ({
    tier: row.tier, candidate: row.candidate,
    prompt: row.prompt.text, reply: row.reply.text,
    source_node: row.reply.nodeId,
  })),
  ordinary_name_mention_excluded: !result.julian.some(row => row.reply.nodeId === 'n1'),
  other_persona_reply_excluded: !result.julian.some(row => row.reply.nodeId === 'n7'),
  requires_human_attribution_review: true,
}, null, 2));
