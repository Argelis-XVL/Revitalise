const { Accordion } = window.RevitaliseDesignSystem_a4dff3;
const FAQS = [
  { question: 'Who is eligible for these grants?', answer: 'Any disabled adult or family carer over the age of 18 can apply for a grant towards a break or experience that would make a meaningful difference to them.' },
  { question: 'When do you open for applications?', answer: 'Applications are open year-round and each month we have a maximum amount of grants we can distribute.' },
  { question: 'How can I apply?', answer: 'Online, via email, or by paper application — quarterly phone application windows are also available.' },
  { question: 'Who makes the decision on who gets funding?', answer: 'Applications are reviewed and approved by our Trustees on a monthly basis.' },
  { question: 'Do I need to have booked my holiday before applying?', answer: 'No — you can apply first, and we pay the provider directly once your grant is approved.' },
];

function FaqScreen() {
  return (
    <div>
      <div style={{ position: 'relative', height: '220px' }}>
        <img src="../../assets/photography/guests-icecream.jpeg" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
        <div style={{ position: 'absolute', left: 0, top: '50%', transform: 'translateY(-50%)', background: 'var(--brand-primary)', padding: 'var(--space-8) var(--space-10)' }}>
          <h1 style={{ fontFamily: 'var(--font-display)', color: '#fff', fontSize: 'var(--text-3xl)' }}>Frequently Asked Questions</h1>
        </div>
      </div>
      <div style={{ padding: 'var(--space-16) var(--space-6)', display: 'flex', justifyContent: 'center' }}>
        <Accordion items={FAQS} />
      </div>
    </div>
  );
}
window.FaqScreen = FaqScreen;
