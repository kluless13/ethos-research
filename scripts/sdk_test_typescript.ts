/**
 * SDK Test: TypeScript (ethos-ts-sdk)
 *
 * Tests the ethos-ts-sdk SDK.
 * 
 * NOTE: The SDK has some endpoint compatibility issues with the current API.
 * This test documents what works and what doesn't.
 *
 * Usage:
 *   npx tsx scripts/sdk_test_typescript.ts
 */

import { Ethos, Profile, Market, Vouch } from 'ethos-ts-sdk';

// ─────────────────────────────────────────────────────────────────────────────
// Test Functions
// ─────────────────────────────────────────────────────────────────────────────

async function testMarkets(client: Ethos, maxMarkets: number = 50): Promise<Market[]> {
  console.log(`\n🏪 Testing Markets (first ${maxMarkets})...`);

  const markets: Market[] = [];
  try {
    // Use the async generator to fetch markets
    for await (const market of client.markets.list()) {
      markets.push(market);
      if (markets.length >= maxMarkets) break;
    }

    console.log(`   ✅ Fetched ${markets.length} markets`);

    // Show some stats
    const withActivity = markets.filter(m => m.trustVotes > 1 || m.distrustVotes > 1).length;
    console.log(`   ✅ Markets with activity: ${withActivity}`);

    // Show top markets by votes
    const top5 = [...markets]
      .sort((a, b) => (b.trustVotes + b.distrustVotes) - (a.trustVotes + a.distrustVotes))
      .slice(0, 5);

    console.log(`\n   📈 Top 5 by votes:`);
    for (const m of top5) {
      console.log(`      Profile ${m.profileId}: trust=${m.trustVotes}, distrust=${m.distrustVotes}`);
    }

    return markets;
  } catch (e: any) {
    console.log(`   ❌ Error: ${e.message}`);
    // SDK issue: endpoint may not match current API
    console.log(`   ℹ️  Note: SDK may have endpoint compatibility issues`);
    return [];
  }
}

async function testTopMarkets(client: Ethos, markets: Market[]): Promise<{ topByVotes: Market[]; mostTrusted: Market[] }> {
  console.log('\n🏆 Analyzing Top Markets...');

  if (markets.length === 0) {
    console.log('   ⚠️  No markets to analyze');
    return { topByVotes: [], mostTrusted: [] };
  }

  try {
    // Sort by total votes
    const topByVotes = [...markets]
      .sort((a, b) => (b.trustVotes + b.distrustVotes) - (a.trustVotes + a.distrustVotes))
      .slice(0, 5);
    console.log(`   ✅ Top 5 by total votes:`);
    for (const m of topByVotes.slice(0, 3)) {
      console.log(`      Profile ${m.profileId}: trust=${m.trustVotes}, distrust=${m.distrustVotes}`);
    }

    // Sort by trust percentage
    const mostTrusted = [...markets]
      .sort((a, b) => (b.trustPrice || 0) - (a.trustPrice || 0))
      .slice(0, 5);
    console.log(`   ✅ Most trusted (by price):`);
    for (const m of mostTrusted.slice(0, 3)) {
      console.log(`      Profile ${m.profileId}: trust_price=${((m.trustPrice || 0) * 100).toFixed(1)}%`);
    }

    return { topByVotes, mostTrusted };
  } catch (e: any) {
    console.log(`   ❌ Error: ${e.message}`);
    return { topByVotes: [], mostTrusted: [] };
  }
}

async function testVouches(client: Ethos, maxVouches: number = 100): Promise<Vouch[]> {
  console.log(`\n🤝 Testing Vouches (first ${maxVouches})...`);

  const vouches: Vouch[] = [];
  try {
    // Use the async generator to fetch vouches
    for await (const vouch of client.vouches.list()) {
      vouches.push(vouch);
      if (vouches.length >= maxVouches) break;
    }

    console.log(`   ✅ Fetched ${vouches.length} vouches`);

    // Count unique relationships
    const pairs = new Set<string>();
    for (const v of vouches) {
      pairs.add(`${v.authorProfileId}->${v.subjectProfileId}`);
    }
    console.log(`   ✅ Unique vouch relationships: ${pairs.size}`);

    // Top vouchers (by count in our sample)
    const voucherCounts = new Map<number, number>();
    for (const v of vouches) {
      voucherCounts.set(v.authorProfileId, (voucherCounts.get(v.authorProfileId) || 0) + 1);
    }

    const topVouchers = [...voucherCounts.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    console.log(`\n   📤 Top vouchers (in sample):`);
    for (const [profileId, count] of topVouchers) {
      console.log(`      Profile ${profileId}: ${count} vouches given`);
    }

    // Top vouchees
    const voucheeCounts = new Map<number, number>();
    for (const v of vouches) {
      voucheeCounts.set(v.subjectProfileId, (voucheeCounts.get(v.subjectProfileId) || 0) + 1);
    }

    const topVouchees = [...voucheeCounts.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    console.log(`\n   📥 Most vouched (in sample):`);
    for (const [profileId, count] of topVouchees) {
      console.log(`      Profile ${profileId}: ${count} vouches received`);
    }

    return vouches;
  } catch (e: any) {
    console.log(`   ❌ Error: ${e.message}`);
    // SDK issue: vouches endpoint uses POST but SDK may use GET
    console.log(`   ℹ️  Note: SDK may have endpoint compatibility issues`);
    return [];
  }
}

async function testProfileLookup(client: Ethos): Promise<Profile | null> {
  console.log('\n🔍 Testing Profile Lookup...');

  const testHandles = ['edoweb3', 'serpinxbt', 'crypsaf'];

  for (const handle of testHandles) {
    try {
      const profile = await client.profiles.getByTwitter(handle);
      console.log(`   ✅ @${handle}:`);
      console.log(`      ID: ${profile.id}`);
      console.log(`      Score: ${profile.score}`);
      console.log(`      XP: ${profile.xpTotal.toLocaleString()}`);
      console.log(`      Vouches received: ${profile.stats?.vouch?.received?.count || 'N/A'}`);
      return profile;
    } catch (e: any) {
      console.log(`   ⚠️  @${handle} not found: ${e.message}`);
    }
  }

  // Note about SDK issue
  console.log(`   ℹ️  Note: SDK uses /profiles/userkey/ but API uses /user/by/x/`);

  return null;
}

async function testVouchLookup(
  client: Ethos,
  profileId: number
): Promise<{ received: Vouch[]; given: Vouch[] }> {
  console.log(`\n🔎 Testing Vouch Lookup for Profile ${profileId}...`);

  try {
    // Vouches received
    const received = await client.vouches.forProfile(profileId);
    console.log(`   ✅ Vouches received: ${received.length}`);

    // Vouches given
    const given = await client.vouches.byProfile(profileId);
    console.log(`   ✅ Vouches given: ${given.length}`);

    return { received, given };
  } catch (e: any) {
    console.log(`   ❌ Error: ${e.message}`);
    return { received: [], given: [] };
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Direct API Test (bypassing SDK issues)
// ─────────────────────────────────────────────────────────────────────────────

async function testDirectAPI(): Promise<{ markets: any[]; vouches: any[]; user: any | null }> {
  console.log('\n📡 Testing Direct API Calls (bypassing SDK)...');
  
  const baseUrl = 'https://api.ethos.network/api/v2';
  const headers = { 'Content-Type': 'application/json', 'X-Ethos-Client': 'ethos-ts-sdk-test' };
  
  const results: { markets: any[]; vouches: any[]; user: any | null } = {
    markets: [],
    vouches: [],
    user: null
  };

  // Test markets endpoint
  try {
    const response = await fetch(`${baseUrl}/markets?limit=5`, { headers });
    const data = await response.json() as { values?: any[] };
    results.markets = data.values || [];
    console.log(`   ✅ Markets: fetched ${results.markets.length} (via GET /markets)`);
  } catch (e: any) {
    console.log(`   ❌ Markets error: ${e.message}`);
  }

  // Test vouches endpoint (POST)
  try {
    const response = await fetch(`${baseUrl}/vouches`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ limit: 5 })
    });
    const data = await response.json() as { values?: any[] };
    results.vouches = data.values || [];
    console.log(`   ✅ Vouches: fetched ${results.vouches.length} (via POST /vouches)`);
  } catch (e: any) {
    console.log(`   ❌ Vouches error: ${e.message}`);
  }

  // Test user lookup endpoint
  try {
    const response = await fetch(`${baseUrl}/user/by/x/edoweb3`, { headers });
    results.user = await response.json();
    console.log(`   ✅ User: found @${results.user?.username} (via GET /user/by/x/)`);
  } catch (e: any) {
    console.log(`   ❌ User error: ${e.message}`);
  }

  return results;
}

// ─────────────────────────────────────────────────────────────────────────────
// Main
// ─────────────────────────────────────────────────────────────────────────────

async function main() {
  console.log('='.repeat(70));
  console.log('SDK TEST: ethos-ts-sdk (TypeScript)');
  console.log('='.repeat(70));
  console.log(`Started at: ${new Date().toISOString()}`);

  // Initialize client
  console.log('\n🚀 Initializing Ethos client...');
  const client = new Ethos();
  console.log(`   ✅ Client ready (base URL: ${client.config.baseUrl})`);

  // Run SDK tests
  const sdkResults: {
    markets?: Market[];
    topMarkets?: { topByVotes: Market[]; mostTrusted: Market[] };
    vouches?: Vouch[];
    profileLookup?: Profile | null;
    vouchLookup?: { received: Vouch[]; given: Vouch[] };
  } = {};

  // 1. Markets (via SDK)
  sdkResults.markets = await testMarkets(client, 50);
  sdkResults.topMarkets = await testTopMarkets(client, sdkResults.markets);

  // 2. Vouches (via SDK)
  sdkResults.vouches = await testVouches(client, 100);

  // 3. Profile lookup (via SDK)
  const profile = await testProfileLookup(client);
  sdkResults.profileLookup = profile;

  // 4. Direct API tests (to verify API works)
  const directResults = await testDirectAPI();

  // Summary
  console.log('\n' + '='.repeat(70));
  console.log('TEST SUMMARY');
  console.log('='.repeat(70));

  console.log('\n📦 SDK Results:');
  const sdkChecks: [string, boolean][] = [
    ['Markets Fetch', (sdkResults.markets?.length ?? 0) > 0],
    ['Top Markets', (sdkResults.topMarkets?.topByVotes?.length ?? 0) > 0],
    ['Vouches Fetch', (sdkResults.vouches?.length ?? 0) > 0],
    ['Profile Lookup', sdkResults.profileLookup !== null],
  ];

  const sdkPassed = sdkChecks.filter(([, ok]) => ok).length;
  console.log(`   Passed: ${sdkPassed}/${sdkChecks.length}`);

  for (const [name, ok] of sdkChecks) {
    const status = ok ? '✅' : '❌';
    console.log(`   ${status} ${name}`);
  }

  console.log('\n📡 Direct API Results:');
  const apiChecks: [string, boolean][] = [
    ['Markets (GET)', directResults.markets.length > 0],
    ['Vouches (POST)', directResults.vouches.length > 0],
    ['User Lookup', directResults.user !== null],
  ];

  const apiPassed = apiChecks.filter(([, ok]) => ok).length;
  console.log(`   Passed: ${apiPassed}/${apiChecks.length}`);

  for (const [name, ok] of apiChecks) {
    const status = ok ? '✅' : '❌';
    console.log(`   ${status} ${name}`);
  }

  if (sdkPassed < sdkChecks.length && apiPassed === apiChecks.length) {
    console.log('\n⚠️  SDK COMPATIBILITY ISSUES DETECTED:');
    console.log('   The SDK endpoints may not match the current Ethos API v2.');
    console.log('   Direct API calls work, but SDK wrapper methods fail.');
    console.log('   Consider updating the SDK or using direct HTTP calls.');
  }

  console.log(`\n🏁 Completed at: ${new Date().toISOString()}`);
}

main().catch(console.error);
