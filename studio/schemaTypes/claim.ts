import {defineField, defineType} from 'sanity'

export const claim = defineType({
  name: 'claim',
  title: 'Claim',
  type: 'document',
  fields: [
    defineField({
      name: 'text',
      title: 'Claim',
      type: 'text',
      rows: 4,
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'sourceType',
      title: 'Source type',
      type: 'string',
      options: {
        list: [
          {title: 'Article', value: 'article'},
          {title: 'Finding', value: 'finding'},
          {title: 'Patch', value: 'patch'},
        ],
        layout: 'radio',
      },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'article',
      title: 'Article',
      type: 'reference',
      to: [{type: 'article'}],
      hidden: ({document}) => document?.sourceType !== 'article',
    }),
    defineField({
      name: 'finding',
      title: 'Finding',
      type: 'reference',
      to: [{type: 'finding'}],
      hidden: ({document}) => document?.sourceType !== 'finding',
    }),
    defineField({
      name: 'patch',
      title: 'Patch',
      type: 'reference',
      to: [{type: 'patch'}],
      hidden: ({document}) => document?.sourceType !== 'patch',
    }),
    defineField({
      name: 'sourceUrl',
      title: 'Source URL',
      type: 'url',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'asOf',
      title: 'As of',
      type: 'date',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'expiresOn',
      title: 'Expires on',
      type: 'date',
      description: 'Date the claim comes due. Null is illegal without expiryStatus = no_expiry_set.',
    }),
    defineField({
      name: 'expiryStatus',
      title: 'Expiry status',
      type: 'string',
      options: {
        list: [
          {title: 'Dated — expiresOn is set', value: 'dated'},
          {title: 'NO_EXPIRY_SET — not forever, we have not dated it', value: 'no_expiry_set'},
        ],
        layout: 'radio',
      },
      validation: (Rule) => Rule.required(),
      description: 'Never treat a missing date as forever. Agent must emit NO_EXPIRY_SET, not STANDING-with-no-clock.',
    }),
    defineField({
      name: 'status',
      title: 'Status',
      type: 'string',
      options: {
        list: [
          {title: 'Standing', value: 'standing'},
          {title: 'Retracted', value: 'retracted'},
          {title: 'Superseded', value: 'superseded'},
          {title: 'Unbuilt', value: 'unbuilt'},
          {title: 'Expired', value: 'expired'},
        ],
        layout: 'radio',
      },
      initialValue: 'standing',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'supersededBy',
      title: 'Superseded by',
      type: 'reference',
      to: [{type: 'claim'}],
      hidden: ({document}) => document?.status !== 'superseded',
    }),
    defineField({
      name: 'evidenceCommand',
      title: 'Evidence command',
      type: 'text',
      rows: 3,
      description: 'The command that proved this claim, when we have one. Empty is allowed; do not invent one.',
    }),
  ],
  preview: {
    select: {title: 'text', subtitle: 'status'},
  },
})
