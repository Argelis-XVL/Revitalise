// Mirrors pages/ApplicationDetailPage.tsx (Revision 15) + CasePanels.tsx + domain/applicationDetailLayout.ts
// (the Trustee Pack's five sections, every row, Pack labels) + VerdictSection.tsx.
// Presentation groups each section's rows by kind (facts, costs, free-text answers, scale answers) for scanning.
const NR = 'Not recorded';
const WITHHELD_NOTE = 'This answer has not been released for trustee review yet.';
const WITHHELD_FULL = 'Every free-text answer is withheld until the process owner has checked its anonymisation and released it, so this is the expected state rather than a fault.';

function SubHeading({ children }) {
  return <h3 style={{ margin: 0, fontSize: 'var(--text-sm)', fontWeight: 700, letterSpacing: '.02em', color: 'var(--ink-700)' }}>{children}</h3>;
}
function Block({ heading, children }) {
  return <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>{heading && <SubHeading>{heading}</SubHeading>}{children}</div>;
}

// Free-text Pack rows (always redacted): the question, then a compact withheld tile.
function Answers({ items }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 'var(--space-3)' }}>
      {items.map(([id, q]) => (
        <div key={id} data-field={id} style={{ borderRadius: '14px', border: '1.5px dashed var(--lavender-200)', background: 'linear-gradient(135deg, rgba(237,232,241,.45), rgba(253,241,248,.45))', padding: 'var(--space-4) var(--space-5)', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
          <p style={{ margin: 0, fontWeight: 700, color: 'var(--text-heading)', fontSize: 'var(--text-sm)', textWrap: 'pretty' }}>{q}</p>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', alignSelf: 'flex-start', background: 'var(--white)', color: window.RV.purple, fontWeight: 700, fontSize: '13px', borderRadius: '999px', padding: '3px 10px' }}><span style={{ width: '7px', height: '7px', borderRadius: '50%', background: window.RV.purple }}></span>Withheld until released</span>
          <p style={{ margin: 0, fontSize: '13px', color: 'var(--ink-700)' }}>{WITHHELD_NOTE}</p>
        </div>
      ))}
    </div>
  );
}

function CostReceipt({ lines, total, after }) {
  const row = (label, value, strong) => (
    <div key={label} style={{ display: 'flex', justifyContent: 'space-between', gap: 'var(--space-4)', padding: '10px 0', borderTop: strong ? '2px solid var(--grey-200)' : '1px solid var(--grey-100)' }}>
      <span style={{ color: strong ? 'var(--text-heading)' : 'var(--ink-700)', fontWeight: strong ? 700 : 400 }}>{label}</span>
      <span style={{ fontVariantNumeric: 'tabular-nums', fontWeight: 700, color: value === NR ? 'var(--ink-600)' : 'var(--text-heading)', fontStyle: value === NR ? 'italic' : 'normal', whiteSpace: 'nowrap' }}>{value}</span>
    </div>
  );
  return (
    <div style={{ borderRadius: '14px', background: 'var(--grey-50)', padding: 'var(--space-2) var(--space-5)' }}>
      <div style={{ marginTop: '-1px' }}>{lines.map(([l, v]) => row(l, v))}</div>
      {row(total[0], total[1], true)}
      {after.map(([l, v]) => row(l, v))}
    </div>
  );
}

// Scale answers (wellbeing): question left, answer pill right.
function AnswerList({ items }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {items.map(([id, q, a], i) => (
        <div key={id} data-field={id} style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: 'var(--space-2) var(--space-4)', padding: '12px 0', borderTop: i ? '1px solid var(--grey-100)' : 'none' }}>
          <span style={{ color: 'var(--text-body)', flex: '1 1 260px' }}>{q}</span>
          <span style={{ background: 'var(--lavender-100)', color: window.RV.purple, fontWeight: 700, fontSize: '13px', borderRadius: '999px', padding: '4px 12px', whiteSpace: 'nowrap' }}>{a}</span>
        </div>
      ))}
    </div>
  );
}

function ScoreBar({ id, label, score }) {
  return (
    <div data-field={id} style={{ borderRadius: '14px', background: 'var(--grey-50)', padding: 'var(--space-4) var(--space-5)', display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 'var(--space-4)', flexWrap: 'wrap' }}>
        <span style={{ fontSize: 'var(--text-sm)', color: 'var(--ink-700)' }}>{label}</span>
        <span style={{ fontFamily: 'var(--font-display)', fontSize: 'var(--text-xl)', color: 'var(--text-heading)' }}>{score == null ? NR : `${score} / 60`}</span>
      </div>
      <div style={{ height: '10px', borderRadius: '999px', background: 'var(--grey-100)', overflow: 'hidden' }}><div style={{ height: '100%', width: `${((score || 0) / 60) * 100}%`, borderRadius: '999px', background: `linear-gradient(90deg, ${window.RV.purple}, var(--brand-primary))` }}></div></div>
    </div>
  );
}

function Scale({ id, question, value }) {
  return (
    <div data-field={id} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <span style={{ color: 'var(--text-body)' }}>{question}</span>
      <div role="img" aria-label={`Answer: ${value} out of 10`} style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
        {Array.from({ length: 11 }, (_, n) => (
          <span key={n} style={{ width: '34px', height: '34px', borderRadius: '50%', display: 'grid', placeItems: 'center', fontSize: '13px', fontWeight: 700, background: n === value ? 'var(--brand-primary)' : 'var(--grey-50)', color: n === value ? 'var(--white)' : 'var(--ink-600)', border: n === value ? 'none' : '1px solid var(--grey-200)' }}>{n}</span>
        ))}
      </div>
    </div>
  );
}

function Restricted({ items }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
      {items.map(([id, q]) => (
        <div key={id} data-field={id} style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: 'var(--space-2) var(--space-4)', borderRadius: '12px', border: '1.5px dashed var(--grey-200)', padding: '10px var(--space-4)' }}>
          <span style={{ color: 'var(--text-heading)', fontWeight: 700, fontSize: 'var(--text-sm)', flex: '1 1 240px' }}>{q}</span>
          <span style={{ background: 'var(--grey-100)', color: 'var(--ink-700)', fontWeight: 700, fontSize: '13px', borderRadius: '999px', padding: '4px 12px' }}>Restricted</span>
        </div>
      ))}
      <p style={{ margin: 0, fontSize: '13px', color: 'var(--ink-700)' }}>Restricted — this field is protected by column-level security and is not requested by this app.</p>
    </div>
  );
}

function Chips({ items }) {
  return <span style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '2px' }}>{items.map((c) => <span key={c} style={{ background: 'var(--white)', border: '1px solid var(--grey-200)', borderRadius: '999px', padding: '2px 10px', fontSize: '13px', fontWeight: 700 }}>{c}</span>)}</span>;
}

function ApplicationDetail({ application, fromGroup, onBackToGroup }) {
  const Button = window.PButton;
  const { Panel, Definitions, PageTitle, ActionRow, RV } = window;
  const [verdict, setVerdict] = React.useState('Approve');
  const a = application;
  const [start = NR, end = NR] = (a.dates || '').split(' to ');
  const exc = a.circ && a.circ !== 'None';

  return (
    <>
      <PageTitle>Application {a.ref}</PageTitle>
      <ActionRow>
        <Button variant="secondary">Print this case</Button>
        {fromGroup && <Button variant="secondary" onClick={onBackToGroup}>Back to group {fromGroup.code}</Button>}
      </ActionRow>

      {/* Summary — S0a–S7 */}
      <window.HeroBand badgeLabel="Score" badgeValue={a.score ?? '—'} eyebrow="Summary" heading={a.score == null ? 'Not scored yet' : `${a.score} out of 60 circumstance points`}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)', alignItems: 'center' }}>
          <window.StatusPill status={a.status} />
          <window.FactChips items={[['Review round', a.round], ['Application ID', a.ref], ['Are you?', 'A disabled person']]} />
        </div>
        <window.FactChips items={[['Start Date', start], ['End Date', end], ['Total requested inc. exceptional funding', exc ? '£1,250.00' : '£1,000.00'], ['Exceptional Funding Amount', exc ? '£250.00' : NR]]} />
      </window.HeroBand>

      <Panel eyebrow="The break" eyebrowColor={RV.purple} heading="Application Details">
        <Definitions items={[
          { label: 'Type of Break', value: 'Holiday accommodation (hotel, cottage, caravan, holiday park)' },
          { label: 'Location of Activity', value: 'Seaside cottage, Northumberland' },
          { label: 'Start Date', value: start },
          { label: 'End Date', value: end },
          { label: 'Exceptional Circumstance', value: exc ? a.circ : NR },
        ]} />
        <Block heading="Costs">
          <CostReceipt
            lines={[['Accommodation or Activity Cost', '£850.00'], ['Travel Costs', '£120.00'], ['Other Costs', '£30.00']]}
            total={['Total Estimated Cost', '£1,000.00']}
            after={[['Amount Requesting Revitalise Individual', '£1,000.00'], ['Exceptional Amount Requested', exc ? '£250.00' : NR]]} />
        </Block>
        <Block heading="In their words">
          <Answers items={[
            ...(a.circ === 'Other (please specify)' ? [['D11a', 'Other exceptional circumstance']] : []),
            ['D12', 'Please briefly explain how this break would benefit you'],
            ['D13', 'Please briefly explain why you’re unable to fund this break yourself?'],
          ]} />
        </Block>
      </Panel>

      <Panel eyebrow="Who they are" eyebrowColor={RV.purple} heading="About Applicant">
        <Definitions items={[
          { label: 'Are you?', value: 'A disabled person' },
          { label: 'Do you or the person you support have a disability as defined by the Equality Act 2010?', value: 'Yes' },
          { label: 'Please select all conditions or illnesses that apply?', value: <Chips items={['Physical disability', 'Other (please specify)']} /> },
          { label: 'As a carer, what type of care and support do you personally provide?', value: NR },
          { label: 'As a carer, on average how many hours of support do you provide a week?', value: NR },
        ]} />
        <Block heading="In their words">
          <Answers items={[['A3a', 'Other condition notes'], ['A4', 'Brief Confirmation'], ['A6', 'Brief Description of Care Support Received or Provided']]} />
        </Block>
      </Panel>

      <Panel eyebrow="How they are doing" eyebrowColor={RV.purple} heading="Current Circumstances">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
          <ScoreBar id="C1" label="Overall Current Circumstances Score (Out of 60)" score={a.score} />
          <Block heading="Life satisfaction"><Scale id="C2" question="Overall, how satisfied are you with your life nowadays? (0 being not at all)" value={2} /></Block>
          <Block heading="In the last 2 weeks…">
            <AnswerList items={[
              ['C3', 'I’ve been feeling optimistic about the future', 'Rarely'],
              ['C4', 'I’ve been feeling useful', 'Some of the time'],
              ['C5', 'I’ve been feeling relaxed', 'None of the time'],
              ['C6', 'I’ve been dealing with problems well', 'Rarely'],
              ['C7', 'I’ve been thinking clearly', 'Some of the time'],
              ['C8', 'I’ve been feeling close to other people', 'Rarely'],
              ['C9', 'I’ve been able to make up my own mind about things', 'Often'],
            ]} />
          </Block>
          <Block heading="In the last year…">
            <AnswerList items={[
              ['C10', 'Go out and do something you enjoy', 'Disagree'],
              ['C11', 'Enjoy other people’s company', 'Agree'],
              ['C12', 'Have a break when you’ve needed one', 'Strongly disagree'],
            ]} />
          </Block>
        </div>
      </Panel>

      <Panel eyebrow="Money" eyebrowColor={RV.purple} heading="Financial Eligibility">
        <Definitions items={[{ label: 'Approximate Household Income', value: '£10,000 – £14,999' }, { label: 'Do you savings over £6,000?', value: 'No' }]} />
        <Block heading="Not visible to trustees">
          <Restricted items={[['F1', 'Do you currently receive means tested benefits?'], ['F2', 'Benefit Provider'], ['F3', 'Are you currently working?']]} />
        </Block>
        <Block heading="In their words">
          <Answers items={[['F5', 'If you have significant care costs, please briefly explain']]} />
        </Block>
      </Panel>

      <Panel eyebrow="From the team" eyebrowColor={RV.purple} heading="Staff recommendation">
        <window.StateMessage heading="No staff recommendation recorded" explanation="No staff recommendation has been written against this application's review record. The rest of the case can still be decided from." />
      </Panel>

      <Panel eyebrow="Your decision" heading="Your verdict">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <p style={{ margin: 0, color: 'var(--text-body)', fontSize: 'var(--text-sm)' }}>You are recording the <strong>Trustee 1</strong> verdict for {a.ref}.</p>
          <window.VerdictChoices name="verdict" value={verdict} onChange={setVerdict} />
          <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: 'var(--text-sm)', color: 'var(--text-heading)' }}>
            Notes (optional)
            <textarea rows={3} style={{ fontFamily: 'var(--font-body)', fontSize: 'var(--text-base)', padding: '12px 14px', borderRadius: '12px', border: '1.5px solid var(--grey-200)', background: 'var(--grey-50)' }}></textarea>
          </label>
          <div><Button variant="primary">Save verdict</Button></div>
        </div>
      </Panel>
    </>
  );
}
window.ApplicationDetail = ApplicationDetail;
