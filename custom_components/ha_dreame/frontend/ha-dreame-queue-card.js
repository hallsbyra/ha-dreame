const Te="modulepreload",Pe=function(r){return"/"+r},ie={},Me=function(e,t,n){let i=Promise.resolve();if(t&&t.length>0){let a=function(u){return Promise.all(u.map(h=>Promise.resolve(h).then(c=>({status:"fulfilled",value:c}),c=>({status:"rejected",reason:c}))))};document.getElementsByTagName("link");const o=document.querySelector("meta[property=csp-nonce]"),l=o?.nonce||o?.getAttribute("nonce");i=a(t.map(u=>{if(u=Pe(u),u in ie)return;ie[u]=!0;const h=u.endsWith(".css"),c=h?'[rel="stylesheet"]':"";if(document.querySelector(`link[href="${u}"]${c}`))return;const m=document.createElement("link");if(m.rel=h?"stylesheet":Te,h||(m.as="script"),m.crossOrigin="",m.href=u,l&&m.setAttribute("nonce",l),document.head.appendChild(m),h)return new Promise((f,S)=>{m.addEventListener("load",f),m.addEventListener("error",()=>S(new Error(`Unable to preload CSS for ${u}`)))})}))}function s(o){const l=new Event("vite:preloadError",{cancelable:!0});if(l.payload=o,window.dispatchEvent(l),!l.defaultPrevented)throw o}return i.then(o=>{for(const l of o||[])l.status==="rejected"&&s(l.reason);return e().catch(s)})};const H=globalThis,J=H.ShadowRoot&&(H.ShadyCSS===void 0||H.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Y=Symbol(),se=new WeakMap;let ye=class{constructor(e,t,n){if(this._$cssResult$=!0,n!==Y)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o;const t=this.t;if(J&&e===void 0){const n=t!==void 0&&t.length===1;n&&(e=se.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),n&&se.set(t,e))}return e}toString(){return this.cssText}};const Le=r=>new ye(typeof r=="string"?r:r+"",void 0,Y),qe=(r,...e)=>{const t=r.length===1?r[0]:e.reduce((n,i,s)=>n+(o=>{if(o._$cssResult$===!0)return o.cssText;if(typeof o=="number")return o;throw Error("Value passed to 'css' function must be a 'css' function result: "+o+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+r[s+1],r[0]);return new ye(t,r,Y)},Ue=(r,e)=>{if(J)r.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const t of e){const n=document.createElement("style"),i=H.litNonce;i!==void 0&&n.setAttribute("nonce",i),n.textContent=t.cssText,r.appendChild(n)}},oe=J?r=>r:r=>r instanceof CSSStyleSheet?(e=>{let t="";for(const n of e.cssRules)t+=n.cssText;return Le(t)})(r):r;const{is:He,defineProperty:De,getOwnPropertyDescriptor:ze,getOwnPropertyNames:Ve,getOwnPropertySymbols:Be,getPrototypeOf:je}=Object,y=globalThis,ae=y.trustedTypes,We=ae?ae.emptyScript:"",Qe=y.reactiveElementPolyfillSupport,k=(r,e)=>r,F={toAttribute(r,e){switch(e){case Boolean:r=r?We:null;break;case Object:case Array:r=r==null?r:JSON.stringify(r)}return r},fromAttribute(r,e){let t=r;switch(e){case Boolean:t=r!==null;break;case Number:t=r===null?null:Number(r);break;case Object:case Array:try{t=JSON.parse(r)}catch{t=null}}return t}},$e=(r,e)=>!He(r,e),le={attribute:!0,type:String,converter:F,reflect:!1,useDefault:!1,hasChanged:$e};Symbol.metadata??(Symbol.metadata=Symbol("metadata")),y.litPropertyMetadata??(y.litPropertyMetadata=new WeakMap);let x=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??(this.l=[])).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=le){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){const n=Symbol(),i=this.getPropertyDescriptor(e,n,t);i!==void 0&&De(this.prototype,e,i)}}static getPropertyDescriptor(e,t,n){const{get:i,set:s}=ze(this.prototype,e)??{get(){return this[t]},set(o){this[t]=o}};return{get:i,set(o){const l=i?.call(this);s?.call(this,o),this.requestUpdate(e,l,n)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??le}static _$Ei(){if(this.hasOwnProperty(k("elementProperties")))return;const e=je(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(k("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(k("properties"))){const t=this.properties,n=[...Ve(t),...Be(t)];for(const i of n)this.createProperty(i,t[i])}const e=this[Symbol.metadata];if(e!==null){const t=litPropertyMetadata.get(e);if(t!==void 0)for(const[n,i]of t)this.elementProperties.set(n,i)}this._$Eh=new Map;for(const[t,n]of this.elementProperties){const i=this._$Eu(t,n);i!==void 0&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const n=new Set(e.flat(1/0).reverse());for(const i of n)t.unshift(oe(i))}else e!==void 0&&t.push(oe(e));return t}static _$Eu(e,t){const n=t.attribute;return n===!1?void 0:typeof n=="string"?n:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??(this._$EO=new Set)).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){const e=new Map,t=this.constructor.elementProperties;for(const n of t.keys())this.hasOwnProperty(n)&&(e.set(n,this[n]),delete this[n]);e.size>0&&(this._$Ep=e)}createRenderRoot(){const e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Ue(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,n){this._$AK(e,n)}_$ET(e,t){const n=this.constructor.elementProperties.get(e),i=this.constructor._$Eu(e,n);if(i!==void 0&&n.reflect===!0){const s=(n.converter?.toAttribute!==void 0?n.converter:F).toAttribute(t,n.type);this._$Em=e,s==null?this.removeAttribute(i):this.setAttribute(i,s),this._$Em=null}}_$AK(e,t){const n=this.constructor,i=n._$Eh.get(e);if(i!==void 0&&this._$Em!==i){const s=n.getPropertyOptions(i),o=typeof s.converter=="function"?{fromAttribute:s.converter}:s.converter?.fromAttribute!==void 0?s.converter:F;this._$Em=i;const l=o.fromAttribute(t,s.type);this[i]=l??this._$Ej?.get(i)??l,this._$Em=null}}requestUpdate(e,t,n,i=!1,s){if(e!==void 0){const o=this.constructor;if(i===!1&&(s=this[e]),n??(n=o.getPropertyOptions(e)),!((n.hasChanged??$e)(s,t)||n.useDefault&&n.reflect&&s===this._$Ej?.get(e)&&!this.hasAttribute(o._$Eu(e,n))))return;this.C(e,t,n)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:n,reflect:i,wrapped:s},o){n&&!(this._$Ej??(this._$Ej=new Map)).has(e)&&(this._$Ej.set(e,o??t??this[e]),s!==!0||o!==void 0)||(this._$AL.has(e)||(this.hasUpdated||n||(t=void 0),this._$AL.set(e,t)),i===!0&&this._$Em!==e&&(this._$Eq??(this._$Eq=new Set)).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??(this.renderRoot=this.createRenderRoot()),this._$Ep){for(const[i,s]of this._$Ep)this[i]=s;this._$Ep=void 0}const n=this.constructor.elementProperties;if(n.size>0)for(const[i,s]of n){const{wrapped:o}=s,l=this[i];o!==!0||this._$AL.has(i)||l===void 0||this.C(i,void 0,s,l)}}let e=!1;const t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(n=>n.hostUpdate?.()),this.update(t)):this._$EM()}catch(n){throw e=!1,this._$EM(),n}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&(this._$Eq=this._$Eq.forEach(t=>this._$ET(t,this[t]))),this._$EM()}updated(e){}firstUpdated(e){}};x.elementStyles=[],x.shadowRootOptions={mode:"open"},x[k("elementProperties")]=new Map,x[k("finalized")]=new Map,Qe?.({ReactiveElement:x}),(y.reactiveElementVersions??(y.reactiveElementVersions=[])).push("2.1.2");const O=globalThis,ue=r=>r,D=O.trustedTypes,ce=D?D.createPolicy("lit-html",{createHTML:r=>r}):void 0,Ae="$lit$",b=`lit$${Math.random().toFixed(9).slice(2)}$`,we="?"+b,Fe=`<${we}>`,w=document,T=()=>w.createComment(""),P=r=>r===null||typeof r!="object"&&typeof r!="function",ee=Array.isArray,Ge=r=>ee(r)||typeof r?.[Symbol.iterator]=="function",W=`[ 	
\f\r]`,C=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,de=/-->/g,he=/>/g,$=RegExp(`>|${W}(?:([^\\s"'>=/]+)(${W}*=${W}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),pe=/'/g,me=/"/g,Se=/^(?:script|style|textarea|title)$/i,Ke=r=>(e,...t)=>({_$litType$:r,strings:e,values:t}),p=Ke(1),E=Symbol.for("lit-noChange"),d=Symbol.for("lit-nothing"),fe=new WeakMap,A=w.createTreeWalker(w,129);function xe(r,e){if(!ee(r)||!r.hasOwnProperty("raw"))throw Error("invalid template strings array");return ce!==void 0?ce.createHTML(e):e}const Xe=(r,e)=>{const t=r.length-1,n=[];let i,s=e===2?"<svg>":e===3?"<math>":"",o=C;for(let l=0;l<t;l++){const a=r[l];let u,h,c=-1,m=0;for(;m<a.length&&(o.lastIndex=m,h=o.exec(a),h!==null);)m=o.lastIndex,o===C?h[1]==="!--"?o=de:h[1]!==void 0?o=he:h[2]!==void 0?(Se.test(h[2])&&(i=RegExp("</"+h[2],"g")),o=$):h[3]!==void 0&&(o=$):o===$?h[0]===">"?(o=i??C,c=-1):h[1]===void 0?c=-2:(c=o.lastIndex-h[2].length,u=h[1],o=h[3]===void 0?$:h[3]==='"'?me:pe):o===me||o===pe?o=$:o===de||o===he?o=C:(o=$,i=void 0);const f=o===$&&r[l+1].startsWith("/>")?" ":"";s+=o===C?a+Fe:c>=0?(n.push(u),a.slice(0,c)+Ae+a.slice(c)+b+f):a+b+(c===-2?l:f)}return[xe(r,s+(r[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),n]};class M{constructor({strings:e,_$litType$:t},n){let i;this.parts=[];let s=0,o=0;const l=e.length-1,a=this.parts,[u,h]=Xe(e,t);if(this.el=M.createElement(u,n),A.currentNode=this.el.content,t===2||t===3){const c=this.el.content.firstChild;c.replaceWith(...c.childNodes)}for(;(i=A.nextNode())!==null&&a.length<l;){if(i.nodeType===1){if(i.hasAttributes())for(const c of i.getAttributeNames())if(c.endsWith(Ae)){const m=h[o++],f=i.getAttribute(c).split(b),S=/([.?@])?(.*)/.exec(m);a.push({type:1,index:s,name:S[2],strings:f,ctor:S[1]==="."?Je:S[1]==="?"?Ye:S[1]==="@"?et:B}),i.removeAttribute(c)}else c.startsWith(b)&&(a.push({type:6,index:s}),i.removeAttribute(c));if(Se.test(i.tagName)){const c=i.textContent.split(b),m=c.length-1;if(m>0){i.textContent=D?D.emptyScript:"";for(let f=0;f<m;f++)i.append(c[f],T()),A.nextNode(),a.push({type:2,index:++s});i.append(c[m],T())}}}else if(i.nodeType===8)if(i.data===we)a.push({type:2,index:s});else{let c=-1;for(;(c=i.data.indexOf(b,c+1))!==-1;)a.push({type:7,index:s}),c+=b.length-1}s++}}static createElement(e,t){const n=w.createElement("template");return n.innerHTML=e,n}}function R(r,e,t=r,n){if(e===E)return e;let i=n!==void 0?t._$Co?.[n]:t._$Cl;const s=P(e)?void 0:e._$litDirective$;return i?.constructor!==s&&(i?._$AO?.(!1),s===void 0?i=void 0:(i=new s(r),i._$AT(r,t,n)),n!==void 0?(t._$Co??(t._$Co=[]))[n]=i:t._$Cl=i),i!==void 0&&(e=R(r,i._$AS(r,e.values),i,n)),e}class Ze{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){const{el:{content:t},parts:n}=this._$AD,i=(e?.creationScope??w).importNode(t,!0);A.currentNode=i;let s=A.nextNode(),o=0,l=0,a=n[0];for(;a!==void 0;){if(o===a.index){let u;a.type===2?u=new q(s,s.nextSibling,this,e):a.type===1?u=new a.ctor(s,a.name,a.strings,this,e):a.type===6&&(u=new tt(s,this,e)),this._$AV.push(u),a=n[++l]}o!==a?.index&&(s=A.nextNode(),o++)}return A.currentNode=w,i}p(e){let t=0;for(const n of this._$AV)n!==void 0&&(n.strings!==void 0?(n._$AI(e,n,t),t+=n.strings.length-2):n._$AI(e[t])),t++}}class q{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,n,i){this.type=2,this._$AH=d,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=n,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=R(this,e,t),P(e)?e===d||e==null||e===""?(this._$AH!==d&&this._$AR(),this._$AH=d):e!==this._$AH&&e!==E&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Ge(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==d&&P(this._$AH)?this._$AA.nextSibling.data=e:this.T(w.createTextNode(e)),this._$AH=e}$(e){const{values:t,_$litType$:n}=e,i=typeof n=="number"?this._$AC(e):(n.el===void 0&&(n.el=M.createElement(xe(n.h,n.h[0]),this.options)),n);if(this._$AH?._$AD===i)this._$AH.p(t);else{const s=new Ze(i,this),o=s.u(this.options);s.p(t),this.T(o),this._$AH=s}}_$AC(e){let t=fe.get(e.strings);return t===void 0&&fe.set(e.strings,t=new M(e)),t}k(e){ee(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let n,i=0;for(const s of e)i===t.length?t.push(n=new q(this.O(T()),this.O(T()),this,this.options)):n=t[i],n._$AI(s),i++;i<t.length&&(this._$AR(n&&n._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){const n=ue(e).nextSibling;ue(e).remove(),e=n}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}}class B{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,n,i,s){this.type=1,this._$AH=d,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=s,n.length>2||n[0]!==""||n[1]!==""?(this._$AH=Array(n.length-1).fill(new String),this.strings=n):this._$AH=d}_$AI(e,t=this,n,i){const s=this.strings;let o=!1;if(s===void 0)e=R(this,e,t,0),o=!P(e)||e!==this._$AH&&e!==E,o&&(this._$AH=e);else{const l=e;let a,u;for(e=s[0],a=0;a<s.length-1;a++)u=R(this,l[n+a],t,a),u===E&&(u=this._$AH[a]),o||(o=!P(u)||u!==this._$AH[a]),u===d?e=d:e!==d&&(e+=(u??"")+s[a+1]),this._$AH[a]=u}o&&!i&&this.j(e)}j(e){e===d?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}}class Je extends B{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===d?void 0:e}}class Ye extends B{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==d)}}class et extends B{constructor(e,t,n,i,s){super(e,t,n,i,s),this.type=5}_$AI(e,t=this){if((e=R(this,e,t,0)??d)===E)return;const n=this._$AH,i=e===d&&n!==d||e.capture!==n.capture||e.once!==n.once||e.passive!==n.passive,s=e!==d&&(n===d||i);i&&this.element.removeEventListener(this.name,this,n),s&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}}class tt{constructor(e,t,n){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=n}get _$AU(){return this._$AM._$AU}_$AI(e){R(this,e)}}const rt=O.litHtmlPolyfillSupport;rt?.(M,q),(O.litHtmlVersions??(O.litHtmlVersions=[])).push("3.3.3");const nt=(r,e,t)=>{const n=t?.renderBefore??e;let i=n._$litPart$;if(i===void 0){const s=t?.renderBefore??null;n._$litPart$=i=new q(e.insertBefore(T(),s),s,void 0,t??{})}return i._$AI(r),i};const I=globalThis;class N extends x{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var t;const e=super.createRenderRoot();return(t=this.renderOptions).renderBefore??(t.renderBefore=e.firstChild),e}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=nt(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return E}}N._$litElement$=!0,N.finalized=!0,I.litElementHydrateSupport?.({LitElement:N});const it=I.litElementPolyfillSupport;it?.({LitElement:N});(I.litElementVersions??(I.litElementVersions=[])).push("4.2.2");const st=new Set(["washing","washing_paused","clean_add_water","charging_completed","returning_to_wash","auto_emptying"]),ot=new Set(["sweeping_and_mopping","sweeping","vacuuming","mopping","spot_cleaning","room_cleaning","segment_cleaning"]),at={water_tank_dry:"clean water tank empty",dirty_water_tank:"dirty water tank full",remove_mop:"remove mop pads",route:"route blocked"};function v(r){return String(r??"").trim().toLowerCase()}function Ee(r,e){const t=new Set(["installed","normal","ok","ready","available"]);return r!=null&&!t.has(v(r))?"Check dirty water tank (full, missing or unavailable)":e!=null&&!t.has(v(e))?"Check clean water tank (empty, missing or unavailable)":null}function Re(r){const e=v(r);return e?e.replaceAll("_"," "):""}function lt(r){const e=v(r);return!e||e==="no_error"||e==="unknown"||e==="unavailable"?null:at[e]??Re(e)}function ut(r){switch(r){case"washing":return"Washing pads";case"washing_paused":return"Washing paused";case"clean_add_water":return"Adding water";case"returning_to_wash":return"Returning to wash";case"auto_emptying":return"Auto-emptying";default:return Re(r)}}function ct(r){if(v(r.queueRunState)!=="running")return null;const e=v(r.vacuumState),t=v(r.robotState),n=v(r.taskStatus),i=lt(r.errorCode),s=Ee(r.dirtyWaterTankStatus,r.cleanWaterTankStatus);if(e==="error")return{phase:"error",label:s??i??"Error",...s?{resumeBlockedReason:s}:{}};if(n==="completed")return{phase:"finishing",label:"Finishing step"};if(s)return{phase:"paused",label:s,resumeBlockedReason:s};if(e==="paused"||v(r.robotStatus)==="paused"||r.paused===!0&&r.running===!1||n.endsWith("_paused"))return{phase:"paused",label:i?`Paused (${i})`:"Paused"};if(st.has(t))return{phase:"preparing",label:ut(t)};if(e==="returning"&&n==="room_cleaning")return{phase:"returning",label:"Returning to base"};if(ot.has(t))switch(t){case"sweeping":case"vacuuming":return{phase:"cleaning",label:"Vacuuming"};case"mopping":return{phase:"cleaning",label:"Mopping"};case"sweeping_and_mopping":return{phase:"cleaning",label:"Vacuuming + mopping"};case"spot_cleaning":return{phase:"cleaning",label:"Spot cleaning"};default:return{phase:"cleaning",label:"Cleaning room"}}return e==="cleaning"?{phase:"cleaning",label:"Cleaning room"}:e==="returning"?{phase:"returning",label:"Returning to base"}:{phase:"unknown",label:"Working"}}function g(r,e){const t=String(r||"").trim();if(!t.startsWith("vacuum."))return null;const n=t.slice(7);return n?`sensor.${n}_${e}`:null}const dt=10,ht=22,te={suction_level:{control:"select",suffix:"suction_level",options:["quiet","standard","strong","turbo"],optionIndexToOverrideValue:r=>r},water_volume:{control:"number",suffix:"wetness_level",values:[1,2,3],stateToOverrideValue:r=>{const e=Number(String(r??"").trim());return Number.isFinite(e)?e<=dt?1:e>=ht?3:2:null}}};function pt(r,e){const t=String(r||"").trim();if(!t.startsWith("vacuum."))return null;const n=t.slice(7);if(!n)return null;const i=te[e];return`${i.control}.${n}_${i.suffix}`}function mt(r,e){const t=te[r];if(t.control==="number")return t.stateToOverrideValue(e);const n=String(e??"").trim().toLowerCase(),i=t.options.indexOf(n);return i<0?null:t.optionIndexToOverrideValue(i)}function ft(r,e,t){return{domain:"ha_dreame",service:"update_running_override",data:{config_entry_id:r,field:e,value:_t(e,t)}}}function _t(r,e){const t=te[r];if(t.control==="number"){const o=t.stateToOverrideValue(e),l=o?t.values.indexOf(o):-1,a=l<0?0:(l+1)%t.values.length;return t.values[a]}const n=String(e??"").trim().toLowerCase(),i=t.options.indexOf(n),s=i<0?0:(i+1)%t.options.length;return t.optionIndexToOverrideValue(s)}const gt=new Set(["blocked","out_of_sync"]);function L(r){return typeof r=="object"&&r!==null&&!Array.isArray(r)}function vt(r){return String(r??"").trim()}function re(r){return vt(r).toLowerCase()}function U(r){return typeof r!="number"||!Number.isFinite(r)||r<0?null:Math.trunc(r)}function bt(r){return typeof r=="boolean"?r:null}function yt(r){return Array.isArray(r)&&r.every(e=>typeof e=="string")?[...r]:null}function $t(r){return L(r)&&Object.values(r).every(e=>typeof e=="string")?{...r}:null}function Q(r,e){return r.filter(t=>t.status===e).length}function At(r){if(!L(r))return null;const e=r.item_id,t=r.room_id,n=r.room_name,i=r.status;return typeof e!="string"||typeof t!="number"||!Number.isFinite(t)||typeof n!="string"||typeof i!="string"?null:{itemId:e,roomId:t,roomName:n,status:i,overrides:L(r.overrides)?{...r.overrides}:{},result:typeof r.result=="string"?r.result:null}}function Ce(r){return gt.has(re(r))}function ne(r){const e=re(r);return e?e==="blocked"?"Route blocked":e==="out_of_sync"?"Out of sync":e==="waiting_for_tanks"?"Waiting for water tanks":e==="needs_attention"?"Needs review":e.charAt(0).toUpperCase()+e.slice(1):"Unknown"}function wt(r){if(!L(r))return[];const e=r.queue_items;return Array.isArray(e)?e.flatMap(t=>{const n=At(t);return n?[n]:[]}):[]}function St(r){const e=r?.attributes,t=wt(e),n=L(e)?e:{};return{runState:re(r?.state)||"unknown",allowRobotCommands:bt(n.allow_robot_commands),allowedActions:yt(n.allowed_actions),blockedReasons:$t(n.blocked_reasons),configEntryId:typeof n.config_entry_id=="string"?n.config_entry_id:null,vacuumEntityId:typeof n.vacuum_entity_id=="string"?n.vacuum_entity_id:null,pendingItems:U(n.pending_items)??Q(t,"pending"),runningItems:U(n.running_items)??Q(t,"running"),completedItems:U(n.completed_items)??Q(t,"completed"),totalItems:U(n.total_items)??t.length,items:t}}const ke={water_volume:[{value:1,label:"Min"},{value:2,label:"Med"},{value:3,label:"Max"},{value:0,label:"Off"}],suction_level:[{value:0,label:"Min"},{value:1,label:"Med"},{value:2,label:"Max"},{value:3,label:"Turbo"},{value:-1,label:"Off"}],repeats:[{value:1,label:"x1"},{value:2,label:"x2"},{value:3,label:"x3"}]},Oe="Default";function Ie(r){if(r==null)return null;if(typeof r=="number")return Number.isFinite(r)?Math.trunc(r):null;if(typeof r=="string"){const e=Number(r.trim());return Number.isFinite(e)?Math.trunc(e):null}return null}function xt(r){return Object.fromEntries(Object.entries(r??{}).filter(([,e])=>e!=null))}function Ne(r,e){const t=Ie(e?.[r]);if(t===null)return Oe;const n=ke[r].find(i=>i.value===t);return n?n.label:String(t)}function Et(r,e){const t=xt(e),n=ke[r],i=Ie(t[r]),s=i===null?-1:n.findIndex(o=>o.value===i);return s<n.length-1?t[r]=n[s+1].value:delete t[r],t}function _e(r){if(typeof r=="number"&&Number.isInteger(r))return r;if(typeof r!="string")return null;const e=r.trim();if(!e)return null;const t=Number(e);return Number.isInteger(t)?t:null}function G(r,e){if(Array.isArray(r)){for(const s of r)G(s,e);return}if(typeof r!="object"||r===null)return;const t=r,n=_e(t.id),i=typeof t.name=="string"?t.name.trim():"";n!==null&&i&&e.push({roomId:n,roomName:i});for(const[s,o]of Object.entries(t)){const l=_e(s);if(l!==null&&typeof o=="string"){const a=o.trim();if(a){e.push({roomId:l,roomName:a});continue}}G(o,e)}}function Rt(r){const e=[];G(r,e);const t=new Map;for(const n of e)t.set(n.roomId,n.roomName);return Array.from(t.entries()).map(([n,i])=>({roomId:n,roomName:i})).sort((n,i)=>n.roomId-i.roomId)}const z="ha-dreame-queue-card",Ct="ha-dreame-queue-card-editor",kt="HA Dreame Queue",Ot="sensor.ha_dreame_queue_status",It="Queue controls are unavailable",ge="Not available right now",K={commands_disabled:"Robot commands disabled",robot_unavailable:"Robot is unavailable",robot_busy:"Waiting for the previous robot task to finish",robot_error:"Robot reports an error",tank_attention:"Check the water tanks",queue_empty:"No rooms are queued",run_active:"Queue is already running",not_running:"Queue is not running",not_interrupted:"Robot is not waiting for user action"},Nt={robot_busy:"Robot is still finishing a previous task. Try again when it is ready."},Tt="The queue command failed. Check Home Assistant for details.";function Pt(r){return typeof r=="string"?K[r]??ge:ge}function Mt(r){const e=j(r)?r.translation_key:void 0;return typeof e!="string"||!(e in K)?Tt:Nt[e]??`${K[e]}.`}const Lt=[{field:"water_volume",label:"Water"},{field:"suction_level",label:"Suction"},{field:"repeats",label:"Repeats"}],qt=[{field:"water_volume",label:"Water"},{field:"suction_level",label:"Suction"}];function Ut(r){return Object.entries(r?.states??{}).filter(([e,t])=>e.startsWith("sensor.")&&Zt(t)).map(([e])=>e).sort()}function Ht(r){return{entity:Ut(r)[0]??Ot}}function Dt(r,e){const t=X(e.title)||kt,n=X(e.entity)||null;if(!n)return ve({title:t,status:"not_configured",entityId:null,message:"Configure a HA Dreame queue status entity."});const i=r?.states[n];if(!i)return ve({title:t,status:"missing",entityId:n,message:"Queue entity not found."});const s=St(i),o=zt(r,s),l=Xt(r,s);return{title:t,status:"ready",entityId:n,message:null,summary:Qt(r,s,o),snapshot:s,activity:o,activeControls:Wt(s,o),canClearPending:s.pendingItems>0&&!Ce(s.runState),rooms:l,rows:Vt(r,s,o)}}function ve({title:r,status:e,entityId:t,message:n}){return{title:r,status:e,entityId:t,message:n,summary:null,snapshot:null,activity:null,activeControls:[],canClearPending:!1,rooms:[],rows:[]}}function zt(r,e){const t=e.vacuumEntityId;if(!r||!t)return null;const n=r.states[t]?.attributes,i=n&&typeof n=="object"?n:{};return ct({queueRunState:e.runState,vacuumState:_(r,t),robotState:_(r,g(t,"state")),taskStatus:_(r,g(t,"task_status")),errorCode:_(r,g(t,"error")),robotStatus:_(r,g(t,"status"))??i.status,paused:i.paused,running:i.running,dirtyWaterTankStatus:_(r,g(t,"dirty_water_tank_status")),cleanWaterTankStatus:_(r,g(t,"clean_water_tank_status"))})}function Vt(r,e,t){const n=e.items,i=Bt(r,e),s=n.flatMap((a,u)=>a.status==="pending"?[u]:[]),o=s[0]??null,l=s[s.length-1]??null;return n.map((a,u)=>({itemId:a.itemId,queuePosition:u,roomName:a.roomName,status:a.status,statusLabel:a.status==="pending"&&e.runState==="waiting_for_tanks"?"Waiting for water tanks":a.status==="pending"?"Queued":a.status==="running"&&t?.phase==="paused"?"Paused":a.status==="running"&&t?.phase==="error"?"Problem":ne(a.status),...a.status==="running"&&i!==null?{progress:i}:{},overrides:{...a.overrides},canRemove:a.status==="pending",canMoveUp:a.status==="pending"&&u!==o,canMoveDown:a.status==="pending"&&u!==l,overrideControls:a.status==="pending"?Gt(a.overrides):Kt(r,e,a)}))}function Bt(r,e){const t=e.vacuumEntityId;if(!r||!t)return null;const n=g(t,"cleaning_progress"),i=be(n?r.states[n]?.state:void 0);if(i!==null)return i;const s=r.states[t]?.attributes;return j(s)?be(s.cleaning_progress):null}function be(r){if(r==null)return null;const e=Number(String(r).trim());return Number.isFinite(e)?Math.max(0,Math.min(100,Math.round(e))):null}function jt(r,e,t){if(r.allowedActions===null)return{...t,disabled:!0,disabledReason:It};if(r.allowedActions.includes(t.service))return t;const n=r.blockedReasons?.[t.service];return{...t,disabled:!0,disabledReason:n==="tank_attention"&&e?.resumeBlockedReason?e.resumeBlockedReason:Pt(n)}}function Wt(r,e){const t=n=>jt(r,e,n);return r.runState==="waiting_for_tanks"?[t({ariaLabel:"Cancel waiting start",label:"Cancel",service:"cancel_queue"})]:Ce(r.runState)?[{ariaLabel:"Reset queue",label:"Reset",service:"clear_pending_queue"}]:r.runState==="running"?e?.phase==="paused"||e?.phase==="error"?[t({ariaLabel:"Continue robot run",label:"Continue",service:"resume_queue"}),t({ariaLabel:"End robot run",label:"End",service:"cancel_queue"})]:[t({ariaLabel:"Cancel queue",label:"Cancel",service:"cancel_queue"}),t({ariaLabel:"Skip current room",label:"Skip",service:"skip_current_room"})]:r.runState==="idle"&&r.pendingItems>0?[t({ariaLabel:"Start queue",label:"Start",service:"start_queue"})]:[]}function Qt(r,e,t){if(t)return t.label;if(e.runState==="idle"&&e.pendingItems>0){const n=Ft(r,e);if(n)return n}switch(e.runState){case"idle":return e.pendingItems===1?"Ready to start 1 room.":e.pendingItems>1?`Ready to start ${e.pendingItems} rooms.`:"Queue is empty.";case"waiting_for_tanks":return"Waiting for water tanks. Starts automatically when the tanks and robot are ready.";case"running":return"Queue is running.";case"completed":return"Queue completed.";case"canceled":return"Queue canceled.";case"blocked":return"Route blocked. Review room access, then reset the queue.";case"out_of_sync":return"Queue out of sync. Review robot state, then reset the queue.";default:return`Queue state: ${ne(e.runState)}.`}}function Ft(r,e){const t=e.vacuumEntityId;if(e.allowedActions?.includes("start_queue")){const n=r&&t?Ee(_(r,g(t,"dirty_water_tank_status")),_(r,g(t,"clean_water_tank_status"))):null;return n?`${n}. Press Start to start automatically after fixing the tanks.`:null}switch(e.blockedReasons?.start_queue){case"robot_unavailable":return"Robot is unavailable. Check its connection before starting.";case"robot_busy":return(r&&t?X(_(r,t)).toLowerCase():"")==="returning"?"Robot is returning to base before the queue can start.":"Robot is finishing a previous task before the queue can start.";case"robot_error":return"Robot reports an error. Check it before starting.";default:return null}}function Gt(r){return Lt.map(e=>({controlType:"pending",field:e.field,label:e.label,valueLabel:Ne(e.field,r)}))}function Kt(r,e,t){return!r||t.status!=="running"||!e.configEntryId||!e.vacuumEntityId?[]:qt.flatMap(n=>{const i=pt(e.vacuumEntityId??"",n.field);if(!i)return[];const s=r.states[i]?.state;if(s===void 0)return[];const o=mt(n.field,s);if(o===null)return[];const l=ft(e.configEntryId??"",n.field,s);return[{controlType:"running",field:n.field,label:n.label,valueLabel:Ne(n.field,{[n.field]:o}),value:l.data.value}]})}function Xt(r,e){const t=e.vacuumEntityId;if(!r||!t)return[];const n=r.states[t]?.attributes;return Rt(j(n)?n.rooms:void 0)}function _(r,e){return e?r.states[e]?.state:void 0}function X(r){return String(r??"").trim()}function j(r){return typeof r=="object"&&r!==null&&!Array.isArray(r)}function Zt(r){const e=r?.attributes;return j(e)&&Array.isArray(e.queue_items)&&typeof e.config_entry_id=="string"}const V=class V extends N{constructor(){super(...arguments),this._config={},this._serviceError=null}static async getConfigElement(){return await Me(()=>import("./ha-dreame-queue-card-editor-lXmQUl9-.js"),[]),document.createElement(Ct)}static getStubConfig(e){return Ht(e)}setConfig(e){if(!e||typeof e!="object")throw new Error("Invalid HA Dreame queue card configuration");this._config={...e}}getCardSize(){return 6}render(){const e=Dt(this.hass,this._config),t=e.snapshot,n=t?.configEntryId;return p`
      <ha-card>
        <div class="header">
          <div>
            <h2 class="title">${e.title}</h2>
            <p class="activity-line">${e.summary??e.entityId??"Queue controls"}</p>
          </div>
          <div class="header-right">
            ${t?this._renderHeaderActions(e.activeControls,e.canClearPending,n):d}
            ${t?p`<span class="state-pill ${t.runState}"
                  >${ne(t.runState)}</span
                >`:d}
          </div>
        </div>

        ${this._serviceError?p`<div class="message service-error">${this._serviceError}</div>`:d}

        ${e.message?p`<div class="message">${e.message}</div>`:p`
              ${e.rooms.length?p`
                    <div class="section-title">Available rooms</div>
                    <div class="room-actions">
                      ${e.rooms.map(i=>p`
                          <button
                            class="room-chip"
                            type="button"
                            ?disabled=${!n}
                            @click=${()=>this._addRoom(n,i.roomId,i.roomName)}
                          >
                            <ha-icon icon="mdi:plus"></ha-icon>
                            ${i.roomName}
                          </button>
                        `)}
                    </div>
                  `:d}
              <div class="queue-list">
                ${e.rows.length?e.rows.map(i=>p`
                        <div class="queue-item ${i.status}">
                          <div class="item-main">
                            <div class="item-headline">
                              <div class="item-title-block">
                                <span class="room-name"
                                  >${i.queuePosition+1}. ${i.roomName}</span
                                >
                                <span class="row-status ${i.status}">${i.statusLabel}</span>
                              </div>
                              ${this._renderQueueItemActions(i,n)}
                            </div>
                            ${i.overrideControls.length?p`
                                  <div class="item-actions">
                                    <div class="override-controls">
                                      ${i.overrideControls.map(s=>this._renderOverrideControl(i.roomName,i.itemId,i.overrides,s,n))}
                                    </div>
                                  </div>
                                `:d}
                            ${i.progress!==void 0?this._renderProgress(i.progress):d}
                          </div>
                        </div>
                      `):p`<div class="empty">Queue is empty.</div>`}
              </div>
            `}
      </ha-card>
    `}_renderProgress(e){return p`
      <div class="progress">
        <div
          aria-label="Room cleaning progress"
          aria-valuemax="100"
          aria-valuemin="0"
          aria-valuenow=${e}
          class="progress-track"
          role="progressbar"
        >
          <div class="progress-fill" style=${`width: ${e}%;`}></div>
        </div>
        <span class="progress-label">${e}%</span>
      </div>
    `}_renderHeaderActions(e,t,n){return!e.length&&!t?d:p`
      <div class="header-actions">
        ${e.map(i=>p`
            <button
              aria-label=${i.ariaLabel}
              class="icon-btn ${i.service==="cancel_queue"?"delete":""}"
              title=${i.disabledReason??i.ariaLabel}
              type="button"
              ?disabled=${!n||i.disabled===!0}
              @click=${()=>this._callQueueService(n,i.service)}
            >
              <ha-icon icon=${this._activeControlIcon(i.service)}></ha-icon>
            </button>
          `)}
        ${t?p`
              <button
                aria-label="Clear pending queue"
                class="icon-btn"
                title="Clear pending queue"
                type="button"
                ?disabled=${!n}
                @click=${()=>this._callQueueService(n,"clear_pending_queue")}
              >
                <ha-icon icon="mdi:playlist-remove"></ha-icon>
              </button>
            `:d}
      </div>
    `}_renderQueueItemActions(e,t){return!e.canMoveUp&&!e.canMoveDown&&!e.canRemove?d:p`
      <div class="item-queue-controls">
        ${e.canMoveUp?p`
              <button
                aria-label=${`Move ${e.roomName} up`}
                class="icon-btn"
                title="Move up"
                type="button"
                ?disabled=${!t}
                @click=${()=>this._moveItem(t,e.itemId,e.queuePosition-1)}
              >
                <ha-icon icon="mdi:arrow-up"></ha-icon>
              </button>
            `:d}
        ${e.canMoveDown?p`
              <button
                aria-label=${`Move ${e.roomName} down`}
                class="icon-btn"
                title="Move down"
                type="button"
                ?disabled=${!t}
                @click=${()=>this._moveItem(t,e.itemId,e.queuePosition+1)}
              >
                <ha-icon icon="mdi:arrow-down"></ha-icon>
              </button>
            `:d}
        ${e.canRemove?p`
              <button
                aria-label=${`Remove ${e.roomName}`}
                class="icon-btn delete"
                title="Remove"
                type="button"
                ?disabled=${!t}
                @click=${()=>this._removeItem(t,e.itemId)}
              >
                <ha-icon icon="mdi:delete"></ha-icon>
              </button>
            `:d}
      </div>
    `}_renderOverrideControl(e,t,n,i,s){return p`
      <button
        aria-label=${`Cycle ${e} ${this._overrideAriaField(i.field)}`}
        class="override-btn"
        title=${`${i.label}: ${i.valueLabel}`}
        type="button"
        ?disabled=${!s}
        @click=${()=>this._cycleOverride(s,t,n,i)}
      >
        <ha-icon icon=${this._overrideIcon(i.field,i.valueLabel)}></ha-icon>
        ${this._renderOverrideValue(i.field,i.valueLabel)}
      </button>
    `}_renderOverrideValue(e,t){if(e==="repeats"||t===Oe)return p`<span>${t}</span>`;const n=e==="water_volume"?3:4;return this._renderBars(n,this._overrideActiveBars(e,t))}_renderBars(e,t){const n=Math.max(0,Math.min(e,t));return p`
      <span class="override-bars" aria-hidden="true">
        ${Array.from({length:e},(i,s)=>{const o=6+s*2,l=s<n;return p`
            <span
              class="override-bar ${l?"active":""}"
              style=${`height:${o}px;`}
            ></span>
          `})}
      </span>
    `}_activeControlIcon(e){return e==="start_queue"||e==="resume_queue"?"mdi:play":e==="skip_current_room"?"mdi:skip-next":e==="clear_pending_queue"?"mdi:restore":"mdi:stop"}_overrideIcon(e,t){return e==="water_volume"?t==="Off"?"mdi:water-off":"mdi:water-percent":e==="suction_level"?t==="Off"?"mdi:fan-off":"mdi:fan":"mdi:repeat"}_overrideActiveBars(e,t){return t==="Off"?0:e==="water_volume"?{Min:1,Med:2,Max:3}[t]??0:e==="suction_level"?{Min:1,Med:2,Max:3,Turbo:4}[t]??0:0}_addRoom(e,t,n){!e||!this.hass?.callService||this.hass.callService("ha_dreame","add_queue_room",{config_entry_id:e,room_id:t,room_name:n})}_removeItem(e,t){!e||!this.hass?.callService||this.hass.callService("ha_dreame","remove_queue_item",{config_entry_id:e,item_id:t})}_moveItem(e,t,n){!e||!this.hass?.callService||this.hass.callService("ha_dreame","move_queue_item",{config_entry_id:e,item_id:t,new_position:n})}async _callQueueService(e,t){if(!(!e||!this.hass?.callService)){this._serviceError=null;try{await this.hass.callService("ha_dreame",t,{config_entry_id:e})}catch(n){this._serviceError=Mt(n)}}}_updateOverrides(e,t,n,i){!e||!this.hass?.callService||this.hass.callService("ha_dreame","update_queue_item_overrides",{config_entry_id:e,item_id:t,overrides:Et(n,i)})}_cycleOverride(e,t,n,i){if(i.controlType==="running"){this._updateRunningOverride(e,i.field,i.value);return}this._updateOverrides(e,t,i.field,n)}_updateRunningOverride(e,t,n){!e||!this.hass?.callService||t==="repeats"||n===void 0||this.hass.callService("ha_dreame","update_running_override",{config_entry_id:e,field:t,value:n})}_overrideAriaField(e){return e==="water_volume"?"water volume":e==="suction_level"?"suction level":"repeats"}};V.properties={hass:{attribute:!1},_config:{state:!0},_serviceError:{state:!0}},V.styles=qe`
    :host {
      display: block;
    }

    ha-card {
      display: block;
      padding: 14px;
    }

    .header {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;
    }

    .header-right {
      align-items: center;
      display: inline-flex;
      gap: 6px;
      min-width: 0;
    }

    .header-actions {
      align-items: center;
      display: inline-flex;
      gap: 4px;
    }

    .title {
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .activity-line {
      color: var(--secondary-text-color);
      font-size: 0.86rem;
      line-height: 1.25;
      margin: 3px 0 0;
      overflow-wrap: anywhere;
    }

    .state-pill {
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.2;
      padding: 4px 9px;
      white-space: nowrap;
    }

    .state-pill.running {
      border-color: var(--state-active-color, #2e7d32);
      color: var(--state-active-color, #2e7d32);
    }

    .state-pill.blocked,
    .state-pill.out_of_sync,
    .state-pill.error {
      border-color: var(--error-color, #d32f2f);
      color: var(--error-color, #d32f2f);
    }

    .message {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      color: var(--secondary-text-color);
      font-size: 0.86rem;
      line-height: 1.35;
      padding: 10px;
    }

    .empty {
      color: var(--secondary-text-color);
      font-size: 0.9rem;
      line-height: 1.35;
    }

    .room-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }

    .section-title {
      color: var(--secondary-text-color);
      font-size: 0.74rem;
      font-weight: 600;
      line-height: 1.2;
      margin: 12px 0 6px;
      text-transform: uppercase;
    }

    .room-chip {
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-family: inherit;
      font-size: 0.84rem;
      line-height: 1;
      max-width: 100%;
      overflow: hidden;
      padding: 7px 11px;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .room-chip:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
    }

    .room-chip:not(:disabled):hover,
    .override-btn:not(:disabled):hover,
    .icon-btn:not(:disabled):hover {
      background: color-mix(in srgb, var(--primary-color, #03a9f4) 10%, transparent);
    }

    .queue-list {
      display: grid;
      gap: 8px;
    }

    .queue-item {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      display: grid;
      gap: 8px;
      grid-template-columns: minmax(0, 1fr);
      padding: 8px 10px;
    }

    .queue-item.running {
      border-color: color-mix(in srgb, var(--state-active-color, #2e7d32) 45%, var(--divider-color));
    }

    .item-main,
    .item-title-block {
      min-width: 0;
    }

    .item-headline {
      align-items: center;
      display: flex;
      gap: 8px;
      justify-content: space-between;
    }

    .room-name {
      display: block;
      font-size: 0.96rem;
      font-weight: 600;
      line-height: 1.25;
      margin: 0;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .row-status {
      color: var(--secondary-text-color);
      font-size: 0.78rem;
      line-height: 1.25;
      text-align: left;
      text-transform: lowercase;
      white-space: nowrap;
    }

    .row-status.running {
      color: var(--state-active-color, #2e7d32);
    }

    .row-status.canceled,
    .row-status.needs_attention,
    .row-status.blocked,
    .row-status.out_of_sync {
      color: var(--error-color, #d32f2f);
    }

    .item-actions {
      align-items: center;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 8px;
    }

    .progress {
      display: grid;
      gap: 4px;
      margin-top: 2px;
    }

    .progress-track {
      background: color-mix(in srgb, var(--divider-color) 55%, transparent);
      border-radius: 999px;
      height: 7px;
      overflow: hidden;
    }

    .progress-fill {
      background: var(--primary-color, #03a9f4);
      height: 100%;
      transition: width 180ms ease-out;
    }

    .progress-label {
      color: var(--secondary-text-color);
      font-size: 0.76rem;
      line-height: 1.2;
    }

    .item-queue-controls {
      align-items: center;
      display: flex;
      gap: 4px;
      justify-content: flex-end;
    }

    .override-controls {
      display: flex;
      flex: 1;
      flex-wrap: wrap;
      gap: 4px;
    }

    .icon-btn {
      align-items: center;
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      display: inline-flex;
      font-family: inherit;
      height: 32px;
      justify-content: center;
      padding: 0;
      width: 32px;
    }

    .icon-btn.delete {
      color: var(--error-color, #d32f2f);
    }

    .icon-btn:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
      opacity: 0.45;
    }

    .override-btn {
      align-items: center;
      background: transparent;
      border: 1px solid var(--divider-color);
      border-radius: 999px;
      color: var(--primary-text-color);
      cursor: pointer;
      display: inline-flex;
      font-family: inherit;
      font-size: 0.72rem;
      gap: 6px;
      justify-content: center;
      line-height: 1.2;
      min-height: 26px;
      min-width: 68px;
      padding: 2px 8px;
      white-space: nowrap;
    }

    .override-btn:disabled {
      color: var(--disabled-text-color, var(--secondary-text-color));
      cursor: default;
      opacity: 0.5;
    }

    .override-bars {
      align-items: flex-end;
      display: inline-flex;
      gap: 2px;
    }

    .override-bar {
      background: color-mix(in srgb, var(--divider-color) 80%, transparent);
      border-radius: 999px;
      width: 3px;
    }

    .override-bar.active {
      background: var(--primary-color, #03a9f4);
    }
  `;let Z=V;customElements.get(z)||customElements.define(z,Z);window.customCards=window.customCards??[];window.customCards.some(r=>r.type===z)||window.customCards.push({type:z,name:"HA Dreame Queue",description:"Queue controls for HA Dreame."});export{Ct as C,kt as D,qe as a,p as b,N as i,Ut as q};
